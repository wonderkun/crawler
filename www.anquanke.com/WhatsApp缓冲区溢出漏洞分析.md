> 原文链接: https://www.anquanke.com//post/id/180459 


# WhatsApp缓冲区溢出漏洞分析


                                阅读量   
                                **248168**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者zimperium，文章来源：blog.zimperium.com
                                <br>原文地址：[https://blog.zimperium.com/whatsapp-buffer-overflow-vulnerability-under-the-scope/](https://blog.zimperium.com/whatsapp-buffer-overflow-vulnerability-under-the-scope/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t014e1894d738d379c8.png)](https://p0.ssl.qhimg.com/t014e1894d738d379c8.png)



## 0x00 前言

5月13日，Facebook公布了WhatsApp中存在的一个漏洞，最近Zimperium发表了关于该漏洞的一篇分析文章。据了解已经有攻击者在实际环境中利用该漏洞，对应的编号为CVE-2019-3568。Zimperium的上一篇[文章](https://blog.zimperium.com/whatsapp-buffer-overflow-vulnerability-reportedly-exploited-wild/)提供了关于该漏洞的一些信息，比如该漏洞影响的WhatsApp产品、可能的利用方式以及Zimperium对该风险的缓解措施。

本文以zLabs的后续研究结果为基础，将与大家分享更多漏洞细节，演示攻击者如何利用WhatsApp上RCE（远程代码执行）漏洞。



## 0x01 背景

在漏洞报告及更新补丁中，Facebook[披露](https://www.facebook.com/security/advisories/cve-2019-3568)该漏洞为远程代码执行漏洞（RCE），影响iOS及Android版的WhatsApp客户端。公告中并没有提及目标平台，并且补丁已推送到所有版本，Android及iOS版更新如下图所示：

[![](https://p3.ssl.qhimg.com/t019c0964030c37ba08.png)](https://p3.ssl.qhimg.com/t019c0964030c37ba08.png)

由于该漏洞技术细节并没有公开，为了保持一致，本文也将从学习角度出发来分析该漏洞。我会有选择地分析更新补丁中的若干个点。

我将尝试梳理该漏洞的一些信息，包括漏洞整体情况、漏洞特征、逻辑，更为重要的是该RCE漏洞对运行在iOS设备上WhatsApp的潜在影响，以及攻击者对该漏洞可能的利用方式。

需要注意的是，本文的分析仍然较为初步，为了充分理解该漏洞，我们还需进一步分析补丁其他方面信息。



## 0x02 补丁分析

由于两个平台上都修复了这个漏洞，并且iOS平台上关于应用分析及逆向工程方面的参考资料较少，因此这里我选择iOS版应用作为目标，希望大家能通过该过程掌握一些经验。

我们的目标是iOS版的WhatsApp客户端。如果大家想一步步跟进，请下载2.19.50版（未打补丁）及2.19.51版（已打补丁）应用。通过diff分析这两个版本（使用IDA、BinDiff或者Ghidra），我们可以看到程序在数据包处理函数方面有所变化，其中两个函数较为重要（`0x100c236b4`以及`0x100c25b78`）。这里我们将逐个分析这两个函数。

### <a class="reference-link" name="0x100c236b4"></a>0x100c236b4

[![](https://p3.ssl.qhimg.com/t01bd6d6365c8ea2732.png)](https://p3.ssl.qhimg.com/t01bd6d6365c8ea2732.png)

首先我们来分析`0x0100C236B4`处的函数（`processBrustPackets`）。该函数似乎负责处理WhatsApp VoIP协议栈中的[STUN](https://www.iana.org/assignments/stun-parameters/stun-parameters.xhtml)及其他突发（burst）数据包。被修复版应用剔除的主要函数片段如下所示：

[![](https://p1.ssl.qhimg.com/t018a668296134dba14.png)](https://p1.ssl.qhimg.com/t018a668296134dba14.png)

[![](https://p4.ssl.qhimg.com/t013c883a70fb6eecbe.png)](https://p4.ssl.qhimg.com/t013c883a70fb6eecbe.png)

在716行，代码会检查`packetSize`及`_Asize`这两个size值，而调用方可以控制这些值。

如果`packetSize`大于`0x7A120`，就会导致整数下溢（underflow），使如下代码段被忽略：

[![](https://p4.ssl.qhimg.com/t01bc649a01ff9ebaa3.png)](https://p4.ssl.qhimg.com/t01bc649a01ff9ebaa3.png)

然后导致程序执行调用方可控的两个`memcpy`（如下图红框标记处）：

[![](https://p2.ssl.qhimg.com/t012ca59248bd4a7a22.png)](https://p2.ssl.qhimg.com/t012ca59248bd4a7a22.png)

在更新版中已删除了这个代码执行段：

[![](https://p1.ssl.qhimg.com/t0196d5094b28dd46d8.png)](https://p1.ssl.qhimg.com/t0196d5094b28dd46d8.png)

打补丁前后相关函数的BinDiff调用图如下所示：

[![](https://p4.ssl.qhimg.com/t01c3bea5d3c1ebfb4b.png)](https://p4.ssl.qhimg.com/t01c3bea5d3c1ebfb4b.png)

### <a class="reference-link" name="0x100c25b78"></a>0x100c25b78

接下来我们分析`0x0100C25B78`处的另一个函数（`handle_incoming_traffic`），被patch前的部分代码如下所示：

[![](https://p0.ssl.qhimg.com/t01cfacd8a21b16186d.png)](https://p0.ssl.qhimg.com/t01cfacd8a21b16186d.png)

在第60行，代码会使用调用方提供的参数来调用`memcpy`，其中并没有检查size，这样可能导致缓冲区溢出漏洞。

patch后的版本中引入了size检查，确保size小于等于`0x5c8`：

[![](https://p0.ssl.qhimg.com/t01f8cb079d419a847a.png)](https://p0.ssl.qhimg.com/t01f8cb079d419a847a.png)

另外前面我们分析的那个函数中也添加了size检查，如下图所示：

[![](https://p3.ssl.qhimg.com/t01b1f246b407b77262.png)](https://p3.ssl.qhimg.com/t01b1f246b407b77262.png)

总结一下，通过二进制diff分析，我们发现官方在这两个函数引入了size检查，修复了可能被利用的内存溢出漏洞。

有趣的是，这两个函数在WhatsApp应用内部的通信过程中都发挥着重要作用，相关调用图如下所示：

[![](https://p1.ssl.qhimg.com/t01735afa30d2b4a943.png)](https://p1.ssl.qhimg.com/t01735afa30d2b4a943.png)

此时，我们知道更新版应用中删除了潜在的缓冲区溢出及整数下溢漏洞，这些漏洞可能用于WhatsApp应用中受调用方控制的远程代码执行场景。接下来，我们需要确认攻击者使用的语音呼叫功能中的确涉及到这些函数。



## 0x03 环境准备

为了验证语音呼叫过程中是否会调用该函数，我们可以在已越狱的设备上，通过Xcode连接存在漏洞的WhatsApp应用：

[![](https://p2.ssl.qhimg.com/t0109924a94838febac.png)](https://p2.ssl.qhimg.com/t0109924a94838febac.png)

在函数地址上设置断点，或者使用Jonatan Levin的[Jtool2](http://newosxbook.com/forum/viewtopic.php?f=3&amp;t=19577)工具为xCode创建断点命令：

[![](https://p1.ssl.qhimg.com/t0192185b868404cfec.png)](https://p1.ssl.qhimg.com/t0192185b868404cfec.png)

效果如下：

[![](https://p1.ssl.qhimg.com/t011b91529c3a61aad7.png)](https://p1.ssl.qhimg.com/t011b91529c3a61aad7.png)

现在向测试账户发起语音呼叫，与预想的一致，断点会被触发：

[![](https://p1.ssl.qhimg.com/t01a872892ba537742e.png)](https://p1.ssl.qhimg.com/t01a872892ba537742e.png)

在进一步动态分析前，我们可以稍微总结一下，梳理此时我们掌握的信息。



## 0x04 初步小结

到目前为止，网上还没有关于完整利用payload的公开信息，也没有关于漏洞利用的技术分析，这是不是有点奇怪呢？

在得出结论之前，有一些事实可供我们参考：

1、Citizen Lab与[金融时报](https://www.ft.com/technology)一起[报道](https://twitter.com/citizenlab/status/1128077054203842566)了相关漏洞信息；

2、WhatsApp在iOS客户端中至少修复了一处（可能多处）潜在的内存破坏漏洞；

3、这些补丁至少涉及到与语音呼叫功能有关的两个函数；

4、无需用户交互即可触发断点；

5、[Google Project Zero](https://docs.google.com/spreadsheets/d/1lkNJ0uQwbeC1ZTRrxdtuPLCIl7mlUreoKfSIgajnSyY/view)认为攻击者可能在实际环境中利用这种方式实现远程代码执行；

6、漏洞公布后iOS操作系统并没有更新补丁。

现在可能还没出现实际攻击活动，人们可能出于某些原因（比如想吸引眼球）才提到这个漏洞。这也能解释为什么现在没有公开payload以及技术分析文章。

另外，根据前文分析，如果攻击的确已经发生，那么可以推测攻击者需要为WhatsApp客户端应用创建一个复杂payload，无需用户交互就能在WhatsApp内部触发远程代码执行功能。

大家可能会思考攻击者会如何利用WhatsApp的RCE漏洞。当然，WhatsApp具备麦克风、摄像头、地址位置以及照片的访问权限，使其成为攻击个人隐私的绝佳目标。然而，访问这些内容需要涉及到各种环节，比如需要在新设备上绕过PAC、Stack-Checks以及iOS引入的其他缓解机制。此外，攻击者还需要在设备重启后维持驻留状态。这种攻击操作可能非常复杂，可能会降低电池寿命、异常重启、让用户收到来自未知号码的语音呼叫等。

如果某些组织或个人经过逆向分析、补丁分析、payload构造、调试及测试后，终于实现了远程代码执行，那么就必须搞定读/写/执行原语（primitive）、充分利用信息泄露及运行时计算才能完成任务。

这个风险太大，攻击者可能不会去尝试。因此我们可以猜测，攻击者可能会针对WhatsApp的其他点进行攻击。

有没有其他快速、高效的方法能实现驻留呢？目标应用中有些代码路径会引用到应用逻辑中隐藏的代码执行功能，攻击者能否利用这些点在重启后维持驻留状态，并且能够远程监控WhatsApp目标账户的活动状态？

这方面仍然没有任何官方数据，与漏洞利用机制一样，这些内容都只能靠我们自己去猜测。

我认为完全符合官方描述的利用过程涉及到“WhatsApp Web”功能。



## 0x05 WhatsApp Web

WhatsApp有个非常受欢迎的web客户端功能：“WhatsApp Web”。利用该功能，用户可以使用浏览器从世界各地连接到WhatsApp账户、发送和接受消息、创建群组、查看历史消息，整个操作与使用正常客户端一样。

为了利用这个远程登录功能，用户需要使用电脑访问[https://web.whatsapp.com](https://web.whatsapp.com/)，通过WhatsApp应用扫描网页上的二维码。

[![](https://p5.ssl.qhimg.com/t014e4de0fb81bccee9.png)](https://p5.ssl.qhimg.com/t014e4de0fb81bccee9.png)

扫描二维码并完成挑战后，服务端会通过浏览器身份认证：

[![](https://p0.ssl.qhimg.com/t010eb9b24ca10a940e.png)](https://p0.ssl.qhimg.com/t010eb9b24ca10a940e.png)

通过认证后，浏览器客户端就能读取每条消息、发送消息，整个过程就像使用设备上的应用一样：

[![](https://p2.ssl.qhimg.com/t01bb2e649528b319ba.png)](https://p2.ssl.qhimg.com/t01bb2e649528b319ba.png)

现在我们要注意一点：在Android设备上，每接入一个账户，用户都能看到一个通知消息，如下所示：

[![](https://p3.ssl.qhimg.com/t01ff69668ed6c31af3.png)](https://p3.ssl.qhimg.com/t01ff69668ed6c31af3.png)

然而在iOS上，WhatsApp客户端会更加静默（至少到目前为止）。如果远程web会话处于激活状态，或者有人劫持了WhatsApp会话，iOS用户并不会看到任何通知。如果我们想看是否有用户劫持当前账户，需要转到设置窗口：

[![](https://p2.ssl.qhimg.com/t017daf46c74ae803bc.png)](https://p2.ssl.qhimg.com/t017daf46c74ae803bc.png)

WhatsApp Web：

[![](https://p0.ssl.qhimg.com/t019be8e3da96aff30a.png)](https://p0.ssl.qhimg.com/t019be8e3da96aff30a.png)

然后我们就可以看到已连接的浏览器列表：

[![](https://p0.ssl.qhimg.com/t010bbce27b846f5454.png)](https://p0.ssl.qhimg.com/t010bbce27b846f5454.png)

在iOS上我们看不到任何IP或标识符信息，只能看到浏览器的`User-Agent`信息。

因此，如果用户账户被远程劫持，在iOS设备上看不到任何通知。

此外，只要用户保持连接，WhatsApp Web就可以维持登录状态，即使目标设备重启也无法影响。

如果攻击者找到WhatsApp中的RCE漏洞，那么这个口看起来似乎是非常完美的目标。



## 0x06 演示

通过逆向身份认证过程，我发现攻击者可以调用目标设备上的某个函数来悄悄认证远程web会话：

```
-[WASettingsViewController qrCodeScannerViewController:didFinishWithCode: ]
```

该函数负责处理新web会话中包含的认证挑战。如果攻击者调用该函数，就能授权当前WhatsApp账户的远程会话连接。

我们可以在Xcode上模拟这个过程：

1、浏览[https://web.whatsapp.com](https://web.whatsapp.com/)，打开WhatsApp Web服务；

2、拷贝二维码挑战，将其转换成字符串；

3、在Xcode中，暂停WhatsApp，拷贝如下命令：

```
(lldb) po [[WASettingsViewController new] qrCodeScannerViewController:[WAWebClientQRCodeScannerViewController new] didFinishWithCode:@”PUT_TARGET_TOKEN_HERE” ]
```

4、大功告成，我们已经悄悄劫持了目标账户。

整个过程可参考[此处视频](https://youtu.be/hwihFtYbthU)，其中攻击者具备WhatsApp应用的远程代码执行权限（这里我们以调试会话来模拟这个攻击场景），然后利用该权限来执行客户端应用中的任意代码。这里攻击者劫持了客户端WhatsApp会话，并且用户没有得到任何通知。



## 0x07 总结

不论实际攻击场景是否与我们设想的场景一致，不论攻击是针对Anroid或者iOS平台，我们依然缺了不少信息。也就是说，我希望这篇文章能帮大家了解iOS上可能存在的攻击方法，理解其特点及局限性，更好理解如何在最新版的iOS设备上，在不影响设备状态的情况下，以最隐蔽的方式利用应用安全漏洞（如RCE）来完成跟踪任务。
