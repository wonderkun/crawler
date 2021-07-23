> 原文链接: https://www.anquanke.com//post/id/87257 


# 【漏洞分析】Foscam C1室内高清摄像机的多个漏洞分析


                                阅读量   
                                **109959**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[http://blog.talosintelligence.com/2017/11/foscam-multiple-vulns.html](http://blog.talosintelligence.com/2017/11/foscam-multiple-vulns.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01abff403e6d7dc2b1.png)](https://p3.ssl.qhimg.com/t01abff403e6d7dc2b1.png)

译者：[eridanus96](http://bobao.360.cn/member/contribute?uid=2857535356)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**摘要**

Foscam C1室内高清摄像头是一个基于网络的摄像头，用于包括家庭安防在内的多种场合。在6月，Talos团队曾发现该设备存在多个漏洞，并与Foscam一同开发了修复补丁，随后在我们的博客中发布了漏洞的详细信息：

[http://blog.talosintelligence.com/2017/06/foscam-vuln-details.html](http://blog.talosintelligence.com/2017/06/foscam-vuln-details.html)

在继续对这些设备进行安全评估的过程中，我们又发现了其它漏洞。根据我们“负责任的披露”原则，我们已经与Foscam进行合作，以确保这些漏洞最终能得以解决，并且可以为受漏洞映像的客户提供固件更新。

借助本次发现的这些漏洞，攻击者可以在受漏洞影响的设备上实现远程代码执行，并可以将恶意固件映像上传至设备，最终可能导致攻击者完全控制该设备。

<br>

**webService DDNS客户端代码执行漏洞**



Foscam C1室内高清摄像机一旦启用了动态DNS（DDNS）功能，就很容易受到多个缓冲区溢出漏洞的攻击。针对启用了DDNS的设备，攻击者可以利用恶意HTTP服务器来进行攻击。

当设备启动时，会产生一个线程，以定期连接到此前配置过的DDNS服务器。该线程会检查是否存在可用更新，同时检查与DDNS服务器相关联的IP地址是否发生变化。在该过程中，设备向DDNS服务器发送请求，随后没有执行边界检查，就将DDNS服务器的响应写入到缓冲区之中。

**如果攻击者能够控制服务器，构建一个大于所分配缓冲区的响应消息并返回，就能导致溢出，从而在设备上实现远程代码执行。**由该问题导致的漏洞如下：

**Foscam IP Video Camera webService oray.com DDNS Client Code Execution Foscam IP Video Camera webService oray.com DDNS Client Code Execution Vulnerability (TALOS-2017-0357 / CVE-2017-2854)**

[https://www.talosintelligence.com/reports/TALOS-2017-0357/](https://www.talosintelligence.com/reports/TALOS-2017-0357/)

**Foscam IP Video Camera webService 3322.net DDNS Client Code Execution Vulnerability (TALOS-2017-0358 / CVE-2017-2855)**

[https://www.talosintelligence.com/reports/TALOS-2017-0358/](https://www.talosintelligence.com/reports/TALOS-2017-0358/)

**Foscam IP Video Camera webService dyndns.com DDNS Client Code Execution Vulnerability (TALOS-2017-0359 / CVE-2017-2856)**

[https://www.talosintelligence.com/reports/TALOS-2017-0359/](https://www.talosintelligence.com/reports/TALOS-2017-0359/)

**Foscam IP Video Camera webService 9299.org DDNS Client Code Execution Vulnerability (TALOS-2017-0360 / CVE-2017-2857)**

[https://www.talosintelligence.com/reports/TALOS-2017-0360/](https://www.talosintelligence.com/reports/TALOS-2017-0360/)

 

**CGIProxy.fcgi固件升级未验证映像漏洞(TALOS-2017-0379 / CVE-2017-2872)**



Foscam C1室内高清摄像机允许通过设备上的Web管理界面进行固件升级，然而该设备并没有对用户提供的固件升级映像文件进行充分的安全验证。

攻击者可以利用这一漏洞，**在受影响的设备上上传并执行自定义的固件映像。**但由于权限限制，攻击者需要登录到管理员权限账户，才可以进行升级操作。

该漏洞编号为CVE-2017-2872，详细信息请参见：

[https://www.talosintelligence.com/reports/TALOS-2017-0379/](https://www.talosintelligence.com/reports/TALOS-2017-0379/) 

**<br>******

**CGIProxy.fcgi模拟AP配置命令执行漏洞 (TALOS-2017-0380 / CVE-2017-2873)**



Foscam C1室内高清摄像机允许配置“模拟AP”（SoftAP），以便在第一次通过Wi-Fi使用时对摄像机进行设置。这一功能可以在Web界面进行配置。HTTP请求首先由CGIProxy.fcgi进程处理，该进程会向相应组件发送消息。当处理“setSoftApConfig”命令时，“webService”中的sub_35FCC函数会被调用。在这里，只有2级权限（管理员）的用户才有权调用此命令。

该函数会从“查询”[1] 中获取参数，随后函数会检查“psk”参数，并要求其长度至少为7个字符[2]，且不包含“n”或“r”字符[3]。最后，使用消息代码“0x607F”将请求转发到另一个组件。

[![](https://p3.ssl.qhimg.com/t016a54ced8f92da56c.png)](https://p3.ssl.qhimg.com/t016a54ced8f92da56c.png)

消息代码“0x607F”将会由devMng中的函数**OnDevMngMsgSetSoftApConfig**来处理。该函数会将固定的SSID和用户提供的PSK复制到“CNetworkService”对象[5]中。随后，在[6]处它会调用另一个函数，修改模拟AP中的配置文件。

[![](https://p5.ssl.qhimg.com/t01c9d64c56c3d9b908.png)](https://p5.ssl.qhimg.com/t01c9d64c56c3d9b908.png)

**sub_3DF44**函数再次复制SSID和PSK，随后，调用负责配置模拟AP的sub_4519C函数。该函数首先在[7]的位置更新文件“**/mnt/mtd/app/config/SoftApConfig.xml**”，然后更新“**/mnt/mtd/app/etc/RT2870AP.dat**”。上述更新操作都是通过系统的**sed**命令来完成。

[![](https://p0.ssl.qhimg.com/t01e3d7d44f799ad4e9.png)](https://p0.ssl.qhimg.com/t01e3d7d44f799ad4e9.png)

由于[9]中的PSK参数由用户控制，攻击者就可以使用这一漏洞来插入任意Shell命令。

**此漏洞需要具有管理员权限的有效用户账户，并借助于“setSoftApConfig”命令访问**，其PoC如下：

[![](https://p4.ssl.qhimg.com/t01a3ad2f2cbc2fef63.png)](https://p4.ssl.qhimg.com/t01a3ad2f2cbc2fef63.png)



**devMng 多摄像头10000端口0x0000命令信息泄露漏洞 (TALOS-2017-0381 / CVE-2017-2874)**



Foscam C1室内高清摄像机允许设备通过UDP端口10000和10001与另一台设备进行通信。这一功能的目的是：方便用户在Web管理界面中看到来自多个设备的视频流。

然而，这些设备存在信息泄露漏洞，**未经身份验证的远程攻击者可以利用此漏洞获取到设备的敏感信息，例如MAC地址、摄像机名称和固件版本。**

该漏洞编号为**CVE-2017-2874**，更多信息请参见：

[https://www.talosintelligence.com/reports/TALOS-2017-0381/](https://www.talosintelligence.com/reports/TALOS-2017-0379/) 。

<br>

**devMng 多摄像头10000端口0x0002命令用户名字段代码执行漏洞 (TALOS-2017-0382 / CVE-2017-2875)**



在Foscam C1设备之间的通信过程中，还存在一个缓冲区溢出漏洞，未经身份验证的远程攻击者可以利用该漏洞实现远程代码执行。

该漏洞是由于**在身份验证的请求过程中，对提交的用户名参数缺少正确的边界检查。**

该漏洞编号为CVE-2017-2875，更多信息请参见：

[https://www.talosintelligence.com/reports/TALOS-2017-0382/](https://www.talosintelligence.com/reports/TALOS-2017-0379/) 。

<br>

**devMng 多摄像头10000端口0x0002命令密码字段代码执行漏洞 (TALOS-2017-0383 / CVE-2017-2876)**



与上一个漏洞原理完全相同，**在身份验证的请求过程中，对提交的密码参数也没有进行完全的边界检查**，从而导致了这一漏洞。

其编号为CVE-2017-2876，更多信息请参见：

[https://www.talosintelligence.com/reports/TALOS-2017-0383/](https://www.talosintelligence.com/reports/TALOS-2017-0379/) 。



**devMng 多摄像头10001端口0x0064命令Empty AuthResetKey漏洞 (TALOS-2017-0384 / CVE-2017-2877)**



同样是在Foscam C1设备之间的通信过程中，未经身份验证的攻击者可以通过向受漏洞影响设备的UDP端口10001发送特定的网络数据包，从而将设备上配置的用户账户信息重置为出厂默认值。

**由于缺少相应的校验机制，因此即使在请求信息中不包含合法的“authResetKey”值，也可以重置用户账户。**

该漏洞编号为CVE-2017-2877，更多信息请参见：

[https://www.talosintelligence.com/reports/TALOS-2017-0384/](https://www.talosintelligence.com/reports/TALOS-2017-0384/) 。

<br>

**CGIProxy.fcgi logout代码执行漏洞 (TALOS-2017-0385 / CVE-2017-2878)**



Foscam C1设备的Web界面需要首先进行身份验证，然后才能访问其中的某些功能。其中的登录和注销操作，是通过CGI调用来实现的。HTTP请求首先由“CGIProxy.fcgi”来处理，该过程将向相关组件传递消息。当处理“logOut”命令时，“webService”中的sub_42CF4函数将被调用。然而，拥有任何权限的用户都可以执行这一命令。（权限最低的是“访客”用户，级别为0。）

该函数从查询中获取“usrName”参数。为了确保最多有0x40[2]个字符存入目标缓冲区[3]中，该操作会使用extract_param[1]来完成。随后，该目标缓冲区会再一次被复制[4]，并且经由一次代码为“0x400A”[5]的IPC调用，将其发送至另一个不同的进程之中。

[![](https://p5.ssl.qhimg.com/t01db174b64987655c7.png)](https://p5.ssl.qhimg.com/t01db174b64987655c7.png)

消息代码“0x400A”由“storage”中的“OnStorageMsgUserLogOut”函数处理，该函数会将由IPC得到的用户名、IP地址以及数字“4”复制到大小为0x2c的结构中，然后传递给一个函数[6]，以记录注销操作。

我们特别注意到，用户名是使用strcpy[7]被复制到结构中的。

**为用户名预留的空间是0x20字节，小于函数sub_42CF4（0x40字节）所能获得的最大空间。**上述缺陷，就足以导致攻击者可以覆盖栈内保存的PC内容。

[![](https://p4.ssl.qhimg.com/t018bf10f5431185ad1.png)](https://p4.ssl.qhimg.com/t018bf10f5431185ad1.png)

**该漏洞至少需要一个“访客”级别以上的用户账户，并且利用“logOut”命令来实现。**下面的PoC可以覆盖已经保存的PC以及计数器%r4，以调用“system("reboot")”命令，可能需要多次尝试才能成功：

[![](https://p4.ssl.qhimg.com/t0195fc1b421123b4fc.png)](https://p4.ssl.qhimg.com/t0195fc1b421123b4fc.png)

 

**UPnP Discovery代码执行漏洞 (TALOS-2017-0386 / CVE-2017-2879)**



Foscam C1设备使用了UPnP协议，用于和网关进行通信，以使摄像机的Web界面可远程访问。在启用UPnP后，设备会每隔30秒向组播地址239.255.255.250的1900端口发送下述UPnP发现消息（UPnP Discovery Message）：

[![](https://p4.ssl.qhimg.com/t01ee3766f8c5f8b723.png)](https://p4.ssl.qhimg.com/t01ee3766f8c5f8b723.png)

当收到对此消息的回复时，设备将对其进行分析，从中提取到控制URL并试图连接，以保证持续的通信。

“webService”中的sub_6DC10函数在专用线程中运行，它会不断尝试通过调用sub_6D9AC[1]函数来发现新的启用UPnP协议的设备，sub_6D9AC函数又会反过来调用sub_6CBD0。

[![](https://p2.ssl.qhimg.com/t01a726f73851647de2.png)](https://p2.ssl.qhimg.com/t01a726f73851647de2.png)

sub_6CBD0函数生成一个UPnP发现消息[2]，并将其[3]发送至多播地址239.255.255.250。当其接收到应答[4]时，将会分析[5]之中的消息。

[![](https://p5.ssl.qhimg.com/t010a8741ac074742db.png)](https://p5.ssl.qhimg.com/t010a8741ac074742db.png)

位于[5]的缓冲区将被复制，并且会检查下列内容：

**在消息中的任意位置，是否包含字符串“200 OK”[6]；**

**在消息中的任意位置，是否包含字符串“http://”；**

**在http://后，是否存在字符串“r”。**

最后，sub_62A08被调用，并将消息中从“http://”开始的内容作为第三个参数传递到“std::string”对象。

[![](https://p1.ssl.qhimg.com/t01b7a9edb4a3299f89.png)](https://p1.ssl.qhimg.com/t01b7a9edb4a3299f89.png)

sub_62A08解析控制URL，并向其发送HTTP请求。为此，控制URL[10]首先被函数sub_62790标记化，它将主机[11]、端口[12]和路径放在三个不同的缓冲区中。然后，对提取的token使用sprintf函数，将其置于200字节[15]大小的目标缓冲区中，从而生成HTTP请求。

[![](https://p4.ssl.qhimg.com/t01c7130f2e7a0b5580.png)](https://p4.ssl.qhimg.com/t01c7130f2e7a0b5580.png)

**由于sprintf对于写入缓冲区的字符长度是没有限制的，同时传递给sprintf的参数并没有对其大小进行检查，因此我们可以使用过长的控制URL来溢出目标缓冲区。**

启用UPnP后，在接收到UPnP发现时，可以使用简单的UDP消息来触发该漏洞。下面的PoC可以使Web服务崩溃：

[![](https://p4.ssl.qhimg.com/t012524b0b776f2de45.png)](https://p4.ssl.qhimg.com/t012524b0b776f2de45.png)

 

**受漏洞影响的版本**



经过测试，我们确认以下Foscam固件版本受到上述所有漏洞影响：

**Foscam 室内网络摄像机 C1 系列**

**系统固件版本: 1.9.3.18**

**应用程序固件版本: 2.52.2.43**

**插件版本: 3.3.0.26**

<br>

**结论**



Foscam C1是市场上最为常见的一个网络摄像机产品。因此，这些设备可能会被部署在敏感的位置。由于该型号的网络摄像机适合于安全监控，所以许多人使用这些设备远程监控他们的家庭、儿童和宠物。

基于此，我们强烈建议用户及时升级固件，保持设备在最新状态，从而确保设备的安全性。

Foscam目前已经发布固件更新，可用来修复上述所有漏洞。受影响设备的用户应该尽快更新到最新版本，以确保自己的设备不受攻击。
