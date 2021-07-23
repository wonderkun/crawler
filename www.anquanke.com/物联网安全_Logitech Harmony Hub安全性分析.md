> 原文链接: https://www.anquanke.com//post/id/132240 


# 物联网安全：Logitech Harmony Hub安全性分析


                                阅读量   
                                **84257**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://www.fireeye.com/
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2018/05/rooting-logitech-harmony-hub-improving-iot-security.html](https://www.fireeye.com/blog/threat-research/2018/05/rooting-logitech-harmony-hub-improving-iot-security.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0187736c1e732f3200.jpg)](https://p0.ssl.qhimg.com/t0187736c1e732f3200.jpg)

## 一、前言

FireEye的Mandiant Red Team最近在Logitech Harmony Hub物联网（IoT）设备上发现了一些漏洞，这些漏洞可以被攻击者利用，通过SSH渠道获得目标设备的root访问权限。Harmony Hub是一款家庭控制系统，用来连接并控制用户家庭环境中的各种设备。在本地网络中利用这些漏洞后，攻击者可以控制连接到Hub的设备，也可以利用Hub做为执行节点，攻击本地网络中的其他设备。由于Harmony Hub所支持的设备较多，包括智能门锁、智能恒温器以及其他智能家居设备等，因此这些漏洞会给用户带来极高的风险。

FireEye在2018年1月向Logitech披露了这些漏洞，Logitech积极响应，与FireEye一起沟通协作，发布固件更新（4.15.96）解决了这些问题。

Red Team发现了如下几个漏洞：

1、未验证证书有效性；

2、不安全的更新过程；

3、生产固件镜像中遗留开发者（developer）调试符号；

4、空的root用户密码。

Red Team组合使用了这几个漏洞，最终获得了Harmony Hub的管理员访问权限。在本文中我们介绍了这些漏洞的发现及分析过程，与大家分享了对消费者设备进行严格安全测试的必要性：现如今公众对设备越来越信任，而这些设备不仅连接到家庭网络中，也会透露关于公众日常生活的各种细节，此时安全形势也更加严峻。



## 二、设备分析

### <a class="reference-link" name="%E8%AE%BE%E5%A4%87%E5%87%86%E5%A4%87"></a>设备准备

已公开的一些[研究报告](https://forum.openwrt.org/viewtopic.php?pid=221373)表明，Harmony Hub的测试点上存在一个UART（universal asynchronous receiver/transmitter，通用异步收发传输器）接口。我们将跳线连接到这些测试点上，这样就能使用TTL转USB串行线路连接到Harmony Hub。初步分析启动过程后，我们发现Harmony Hub会通过U-Boot 1.1.4启动，运行一个Linux内核，如图1所示。

[![](https://p4.ssl.qhimg.com/t012087d4c9e6e30ee3.png)](https://p4.ssl.qhimg.com/t012087d4c9e6e30ee3.png)

图1. 从UART接口获得的启动日志

在启动过程后续阶段中，控制台不再输出任何信息，因为内核并没有配备任何控制台接口。我们在U-Boot中重新配置了内核启动参数，想查看完整的启动过程，但并没有恢复出有用的信息。此外，由于设备将UART接口配置成仅传输模式，因此我们不能通过该接口与Harmony Hub进一步交互，因此我们将研究重点转移到了Harmony Hub所运行的Linux操作系统上，想进一步了解整个系统以及其上运行的相关软件。

### <a class="reference-link" name="%E5%9B%BA%E4%BB%B6%E6%81%A2%E5%A4%8D%E5%8F%8A%E6%8F%90%E5%8F%96"></a>固件恢复及提取

Harmony Hub可以使用配套的Android或者iOS应用通过蓝牙来进行初始化配置。我们使用hostapd创建了一个无线网络，在Android测试设备上安装了Burp Suite Pro CA证书，以捕捉Harmony移动应用发往互联网以及发往Harmony Hub的通信流量。一旦初始化配对完成，Harmony应用就会搜索本地网络中的Harmony Hub，使用基于HTTP的API与Harmony Hub通信。

一旦成功连接，Harmony应用就会向Harmony Hub的API发送两个不同的请求，以便Harmony Hub检查是否存在更新，如图2所示。

[![](https://p1.ssl.qhimg.com/t016c85114011a7a613.png)](https://p1.ssl.qhimg.com/t016c85114011a7a613.png)

图2. 使Harmony Hub检查更新的请求报文

Harmony Hub会向Logitech服务器发送当前的固件版本，以确定是否存在更新（如图3所示）。如果需要更新，Logitech服务器会发送一个响应包，其中包含新固件版本所对应的一个URL（如图4所示）。由于我们使用了自签名的证书来捕捉Harmony Hub发送的HTTPS流量，因此我们可以顺利观察到这个过程（Harmony Hub会忽略无效的SSL证书）。

[![](https://p1.ssl.qhimg.com/t01375c1117ad990c51.png)](https://p1.ssl.qhimg.com/t01375c1117ad990c51.png)

图3. Harmony Hub检查固件更新

[![](https://p2.ssl.qhimg.com/t01839b84363df0849c.png)](https://p2.ssl.qhimg.com/t01839b84363df0849c.png)

图4. 服务器返回的响应包中包含更新固件的URL

我们获取了这个固件并检查了相关文件。剥离好几个压缩层后，我们可以在harmony-image.squashfs文件中找到固件。固件所使用的文件系统镜像为SquashFS文件系统，采用lzma压缩算法（这是嵌入式设备常用的压缩格式）。然而，厂商经常使用老版本的squashfstools，这些版本与最新的squashfstools并不兼容。我们使用了[firmware-mod-kit](https://github.com/rampageX/firmware-mod-kit)中的**unsqashfs_all.sh**脚本，自动化探测unsquashfs的正确版本，以便提取文件系统镜像，如图5所示。

[![](https://p2.ssl.qhimg.com/t018d482ec15bdcbde5.png)](https://p2.ssl.qhimg.com/t018d482ec15bdcbde5.png)

图5. 使用firmware-mod-kit提取文件系统

提取文件系统内容后，我们检查了Harmony Hub搭载的操作系统的某些详细配置信息。经过检查后，我们发现这个生产镜像中包含大量的调试信息，比如没有删掉的内核模块等，如图6所示。

[![](https://p2.ssl.qhimg.com/t011e3ef395378dfc19.png)](https://p2.ssl.qhimg.com/t011e3ef395378dfc19.png)

图6. 文件系统中未删掉的Linux内核对象

检查`/etc/passwd`后，我们发现root用户并没有设置密码（如图7所示）。因此，如果我们可以启用dropbear SSH服务器，我们就能通过SSH接口获取Harmony Hub的root访问权限，无需使用密码。

[![](https://p2.ssl.qhimg.com/t01b1bbd1da0ca7a1e3.png)](https://p2.ssl.qhimg.com/t01b1bbd1da0ca7a1e3.png)

图7. `/etc/passwd`文件显示root用户未设置密码

我们发现，如果文件系统中存在`/etc/tdeenable`文件，则会在初始化阶段中启用dropbear SSH服务器，如图8所示。

[![](https://p1.ssl.qhimg.com/t01451ca1c8c3ab6e1d.png)](https://p1.ssl.qhimg.com/t01451ca1c8c3ab6e1d.png)

图8. 如果存在`/etc/tdeenable`，`/etc/init.d/rcS`脚本则会启用dropbear SSH服务器

### <a class="reference-link" name="%E5%8A%AB%E6%8C%81%E6%9B%B4%E6%96%B0%E8%BF%87%E7%A8%8B"></a>劫持更新过程

在初始化过程中，Harmony Hub会在Logitech API上查询**GetJson2Uris**地址，获取各种过程所需的一个URL列表（如图9所示），其中包括检查固件更新所使用的URL以及获取更新所需的额外软件包信息的URL。

[![](https://p2.ssl.qhimg.com/t017c113a31ccc10670.png)](https://p2.ssl.qhimg.com/t017c113a31ccc10670.png)

图9. 发送请求获取各种过程所需的URL地址

我们拦截并修改了服务器返回的响应数据包中的JSON对象，将其中的**GetUpdates**成员指向我们自己的IP地址，如图10所示。

[![](https://p1.ssl.qhimg.com/t01c30dbf5e3c286cb0.png)](https://p1.ssl.qhimg.com/t01c30dbf5e3c286cb0.png)

图10. 修改过的JSON对象

与固件更新过程类似，Harmony Hub会向**GetUpdates**所指定的端点发送一个POST请求，请求中包含设备内部软件包的当前版本信息。**HEOS**软件包对应的请求如图11所示。

[![](https://p0.ssl.qhimg.com/t01beeb83f841abf64a.png)](https://p0.ssl.qhimg.com/t01beeb83f841abf64a.png)

图11. 包含系统中“HEOS”软件包当前版本信息的JSON请求对象

如果POST请求正文中的**sysBuild**参数与服务器已知的当前版本不匹配，服务器就会响应一个初始数据包，其中包含新软件包版本信息。由于某些不知名的原因，Harmony Hub忽略了这个初始响应包，发送了第二个请求。第二个响应包中包含多个URL地址，这些地址指向了新的软件包，如图12所示。

[![](https://p3.ssl.qhimg.com/t01a4c5b7672808fcfb.png)](https://p3.ssl.qhimg.com/t01a4c5b7672808fcfb.png)

图12. 包含软件更新包的JSON响应数据

我们下载了响应数据包中列出的**.pkg**文件，检查后发现这些文件其实是ZIP压缩文件。压缩文件的文件结果比较简单，如图13所示。

[![](https://p1.ssl.qhimg.com/t0176b6a12e4c2f45fa.png)](https://p1.ssl.qhimg.com/t0176b6a12e4c2f45fa.png)

图13. `.pkg`压缩文档结构

其中，**manifest.json**文件可以告诉Harmony Hub在更新过程中如何处理压缩文档的内容，如图14所示。

[![](https://p0.ssl.qhimg.com/t01de9b4990299feb44.png)](https://p0.ssl.qhimg.com/t01de9b4990299feb44.png)

图14. `manifest.json`文件内容

manifest文件中**installer**参数所指定了一个脚本，如果压缩文件中存在该脚本，那么Harmony Hub在更新过程中就会执行这个脚本。我们修改了这个脚本，如图15所示，修改后该脚本会创建`/etc/tdeenable`文件，前面提到过，这样启动过程就会启用SSH接口。

[![](https://p3.ssl.qhimg.com/t01456018c0c3d86b1c.png)](https://p3.ssl.qhimg.com/t01456018c0c3d86b1c.png)

图15. 修改后的`update.sh`文件

我们创建了带有**.pkg**扩展名的一个恶意压缩文档，使用本地web服务器托管该文档。当下一次Harmony Hub根据被篡改的**GetJson2URIs**响应包中给出的URL地址来检查更新时，我们返回经过修改的响应包，指向这个更新文件。Harmony Hub会接收我们提供的恶意软件更新包，重启Harmony Hub后就会启用SSH接口。这样我们就可以使用**root**用户名以及空密码来访问该设备，如图16所示。

[![](https://p0.ssl.qhimg.com/t01a45b5161e9a7d43e.png)](https://p0.ssl.qhimg.com/t01a45b5161e9a7d43e.png)

图16. 重启后设备启用了SSH接口



## 三、总结

随着科技逐步融入我们的日常生活中，我们也在不知不觉中越来越信任各种设备。Harmony Hub与许多物联网设备一样，采用了通用处理器架构，因此攻击者可以轻松将恶意工具添加到被攻破的Harmony Hub上，进一步扩大攻击活动的影响力。Logitech与我们的团队积极合作，发布了4.15.96固件解决了这些漏洞。如果用户对某些设备非常信任，那么这些设备的开发者就应该保持警惕，移除让用户处于危险境地的潜在攻击因素。Logitech在与Red Team的研究工作中发表过一则声明，在此我们也想与大家一起分享：

“Logitech非常重视客户的安全及隐私。2018年1月下旬，FireEye发现了可能影响Logitech Harmony Hub产品的一些漏洞，如果某个恶意黑客已经获取Hub用户网络的访问权限，就可以利用这些漏洞。我们非常感谢FireEye等专业安全研究公司在挖掘探索IoT设备上这类漏洞所付出的努力。

在FireEye将这些研究成果告知我们后，我们第一时间启动了内部调查，并且马上开始研发固件以解决这些问题。4月10日，我们发布了固件更新，全部解决了这些漏洞。如果还有客户没有将固件更新到4.15.96版，我们建议您检查MyHarmony软件，同步基于Hub的远程设备并接收该固件。用户可以查看[此链接](https://support.myharmony.com/en-us/how-to-update-your-firmware)了解关于固件更新的完整说明。

基于Hub的产品包括： Harmony Elite、Harmony Home Hub、Harmony Ultimate Hub、harmony Hub, Harmony Home Control、Harmony Pro、Harmony Smart Control、Harmony Companion、Harmony Smart Keyboard、Harmony Ultimate以及Ultimate Home”。
