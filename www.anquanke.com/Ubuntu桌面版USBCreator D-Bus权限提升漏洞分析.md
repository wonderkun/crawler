> 原文链接: https://www.anquanke.com//post/id/181937 


# Ubuntu桌面版USBCreator D-Bus权限提升漏洞分析


                                阅读量   
                                **196400**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者paloaltonetworks，文章来源：unit42.paloaltonetworks.com
                                <br>原文地址：[https://unit42.paloaltonetworks.com/usbcreator-d-bus-privilege-escalation-in-ubuntu-desktop/](https://unit42.paloaltonetworks.com/usbcreator-d-bus-privilege-escalation-in-ubuntu-desktop/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0192d9a10ad4f5c1a0.jpg)](https://p2.ssl.qhimg.com/t0192d9a10ad4f5c1a0.jpg)



## 0x00 前言

USBCreator D-Bus接口中存在一个漏洞，如果具备`sudoer`组用户的访问权限，那么攻击者可以利用该漏洞绕过`sudo`程序强制的密码安全策略。攻击者能够利用该漏洞，以`root`身份使用任意内容覆盖任意文件，且无需提供密码。这种方式通常会导致权限提升问题，比如攻击者可以覆盖shadow文件，为`root`设置密码。Unit 42向Ubuntu反馈了该漏洞，官方在6月份推出了相应的软件包，[修复](https://bugs.launchpad.net/ubuntu/+source/policykit-desktop-privileges/+bug/1832337)了这个问题。



## 0x01 D-Bus简介

Ubuntu桌面版使用D-Bus作为进程间通信（IPC）媒介。在Ubuntu系统中，总共有2类并发运行的消息总线：一类是系统（system）总线，主要由特权服务使用，用来对整个系统范围提供相关服务；另一类是每个登录用户的会话（session）总线，只对外提供与该特定用户相关的服务。由于我们的目标是提升权限，因此我们主要关注系统总线，因为相关服务会以较高权限（比如`root`）运行。需要注意的是，在D-Bus架构中每个会话总线都会对应一个“路由器（router）”，该路由器会将客户端消息重定向到与之交互的相关服务，客户端需要指定消息发送的服务地址。

每个服务都由对外公开的对象（object）和接口（interface）来定义。在标准的OOP（面向对象编程）语言中，我们可以将对象看成类的接口。每个接口由对应的对象路径所确定，对象路径是类似文件系统路径的一个字符串，可以唯一标识服务对外公开的每个对象。在这种场景中，我们研究过程需要用到的一个标准接口是`org.freedesktop.DBus.Introspectable`接口。该接口中只包含一个方法：`Introspect`。`Introspect`方法会以XML格式返回该对象所支持的方法、信号（signal）以及属性。在本文中我们重点关注的是相关方法，不用分析属性和信号。

我使用了两款工具来与D-Bus接口交互：`gdbus`，这是一款CLI工具，方便在脚本中调用D-Bus提供的方法；以及[**D-Feet**](https://wiki.gnome.org/Apps/DFeet)，这是基于Python的一款GUI工具，可以帮助我们枚举每个总线上可用的服务，查看每个服务包含哪些对象。

[![](https://p0.ssl.qhimg.com/t012670c04732a98221.png)](https://p0.ssl.qhimg.com/t012670c04732a98221.png)

图1. D-Feet主界面

[![](https://p3.ssl.qhimg.com/t012deb95fc81272569.png)](https://p3.ssl.qhimg.com/t012deb95fc81272569.png)

图2. D-Feet接口界面

D-Feet是一款非常好的工具，在整个研究过程中不可或缺。在图1左侧窗口中，我们可以看到D-Bus系统总线已注册的各种服务（请注意我们要在顶部栏选择“System Bus”按钮）。选择`org.debin.apt`服务后，D-Feet会自动查询该服务对应的所有可用对象。一旦我们选择特定的对象，该工具就会列出所有的接口，以及对应的方法、属性、信号，如图2所示。值得一提的是，我们也能获取公开的每个IPC方法的签名（signature）。

我们也可以看到托管每个服务的进程的PID以及对应的命令行参数。这是非常有用的一个功能，我们可以验证目标服务的确以较高权限在运行。系统总线上的某些服务并没有以`root`权限运行，研究起来价值不大。

D-Feet也可以用来调用各种方法。在“Method input”栏中，我们可以指定一系列Python表达式，以逗号分割。这些表达式会被当成被调用函数的参数，如图3所示。Python类型会被封装成D-Bus类型，传递给目标服务。

[![](https://p4.ssl.qhimg.com/t01a0537607e67a91d9.png)](https://p4.ssl.qhimg.com/t01a0537607e67a91d9.png)

图3. 通过D-Feet调用D-Bus方法

某些方法在调用之前需要通过身份认证。我们可以忽略这些方法，因为我们的目标是在不使用凭据的前提下实现权限提升。

[![](https://p2.ssl.qhimg.com/t01c84ce582cebb84c2.png)](https://p2.ssl.qhimg.com/t01c84ce582cebb84c2.png)

图4. 需要身份认证的某个方法

此外还有一些服务会查询另一个D-Bus服务（`org.freedeskto.PolicyKit1`），询问用户是否可以执行某些操作。下文中我们会再讨论这方面内容。



## 0x02 漏洞分析

在研究各种D-Bus服务时，我的目标是寻找以非特权用户身份运行的特权服务，并且这些服务无需身份认证，受用户可控的输入数据影响，可以影响具体的操作。如果没有对用户进行正确的过滤和验证，那么即便执行简单的操作（比如运行程序或者执行某些文件系统I/O操作），也可能导致系统被攻击者突破。

存在漏洞的服务为`com.ubuntu.USBCreator`。`/com/ubuntu/USBCreator`对象中包含一个`Image`方法，Ubuntu系统会在USB Creator工具中用到该方法。

[![](https://p0.ssl.qhimg.com/t01f36e76c92eef6bbd.png)](https://p0.ssl.qhimg.com/t01f36e76c92eef6bbd.png)

图5. `com.ubuntu.USBCreator`服务

[![](https://p2.ssl.qhimg.com/t014969381c9b1e4233.png)](https://p2.ssl.qhimg.com/t014969381c9b1e4233.png)

图6. `/com/ubuntu/USBCreator`对象的`Image`方法

检查该服务，可以看到该服务的确以较高权限运行：

[![](https://p1.ssl.qhimg.com/t01618a263a23c4f7db.png)](https://p1.ssl.qhimg.com/t01618a263a23c4f7db.png)

图7. 服务以高权限运行

由于该服务使用Python语言开发，我们很容易就能查看相关的源代码。首先我们注意到与该方法交互时需要用到`com.ubuntu.usbcreator.image`。从源代码中可知，该服务会查询polkit，确认发起请求的用户是否有权执行该操作（第172行）。

[![](https://p5.ssl.qhimg.com/t014ea114a79ecf47b0.png)](https://p5.ssl.qhimg.com/t014ea114a79ecf47b0.png)

图8. USBCreator源代码

检查polkit的配置文件，如图9所示，我们可以看到`sudo`这个Unix组可以执行该功能。相关文件位于`/var/lib/polkit-1/localauthority`目录中，我们正在分析的文件具体路径为`/var/lib/polkit-1/localauthority/10-vendor.d/com.ubuntu.desktop.pkla`。

[![](https://p0.ssl.qhimg.com/t018a1dd8647a6602ec.png)](https://p0.ssl.qhimg.com/t018a1dd8647a6602ec.png)

图9. 从第26行开始可知哪些组允许访问`com.ubuntu.usbcreator.image`功能

检查服务的源代码后，我们可知其中包含`dd`的Python版实现，`dd`工具可以用来在不同位置之间拷贝文件。然而，这里传递给`_builtin_dd`方法的输入数据直接来自于用户的输入数据。此外，代码也没有对源路径或者目标路径进行检查，不会弹出密码输入提示，这样攻击者就能以`root`身份覆盖文件系统上的任意文件，不需要输入密码，如图10所示。

[![](https://p2.ssl.qhimg.com/t014d63454253580adc.png)](https://p2.ssl.qhimg.com/t014d63454253580adc.png)

图10. 无需输入密码以`root`身份创建文件



## 0x03 总结

目前我们并不清楚是否有攻击者在实际环境中利用了这个漏洞。打上6月18日的补丁后，现在如果我们在Ubuntu系统中启动USBCreator，那么就会看到一个密码认证框。Palo Alto Networks提供的端点防护及响应服务能够阻止攻击者利用该漏洞。
