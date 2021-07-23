> 原文链接: https://www.anquanke.com//post/id/167866 


# 针对WhatsApp、Telegram及Signal应用的侧信道攻击技术研究


                                阅读量   
                                **304264**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者talosintelligence，文章来源：blog.talosintelligence.com
                                <br>原文地址：[https://blog.talosintelligence.com/2018/12/secureim.html](https://blog.talosintelligence.com/2018/12/secureim.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01a1fbc436052ad51a.png)](https://p0.ssl.qhimg.com/t01a1fbc436052ad51a.png)



## 一、前言

从互联网诞生以来，消息应用就一直伴随我们左右。然而最近一段时间，由于一些国家开始实施大规模监控策略，有更多的用户选择安装名为“安全即时通信应用”的端到端加密应用。这些应用声称可以加密用户的邮件、保护用户数据免受第三方危害。

然而，深入分析三款安全消息应用（即Telegram、WhastApp以及Signal）后，我们发现服务商可能无法信守各自的承诺，用户的机密信息可能存在安全风险。

考虑到用户之所以下载这些应用，是因为想让自己的照片和消息完全避免第三方威胁，因此这是一个严重的问题。这些应用拥有海量用户，无法保证这些用户都经过安全教育，很难都了解启用某些设置可能会带来的安全风险。因此，这些应用有义务向用户阐述安全风险，并且在可能的情况下，尽量默认使用更为安全的设置。这些应用会将安全性交由操作系统来负责，在本文中，我们将给大家展示攻击者如何通过侧信道攻击操作系统来破坏这些应用的安全性。本文深入分析了这些应用处理用户数据的背后原理，并没有深入分析这些企业自身的安全性。



## 二、安全消息应用

安全消息应用的背后原理在于所有通信数据都经过用户端点之间加密处理，没有涉及第三方。这意味着服务提供商在任何时间都不具备读取用户数据的能力。

为了实现端到端加密，这些应用要么会开发自己的加密协议，要么采用第三方协议。这些应用通常会使用两种协议：由Telegram安全消息应用开发的MT协议以及由Open Whisper Systems软件公司开发的Signal协议。由于MT协议并没有开源，因此其他应用大多会使用Signal协议或者采用该协议的修改版。其他协议会根据用户的请求来使用该协议（但默认情况下没有使用该协议），这不在本文分析范围中。Facebook Messenger以及Google Allo采用就是这种解决方案，前者具备名为“Secret Conversations”（秘密对话）的一种功能，后者具备名为“Incognito”（隐身）聊天的一种功能。之前研究人员已经分析过公开的源代码，也对实时通信数据做过黑盒分析。

然而，安全消息应用远不止加密协议这么简单。还有其他组件（如UI框架、文件存储模型、群注册机制等）可能是潜在的攻击目标。Electron框架中发现的CVE 2018-1000136[漏洞](https://www.trustwave.com/Resources/SpiderLabs-Blog/CVE-2018-1000136---Electron-nodeIntegration-Bypass/)就是一个很好的例子，WhatsApp和Signal都使用这个框架来构建用户接口。在最糟糕的情况下，攻击者可以利用这个漏洞远程执行代码，或者复制消息。

这些协议的关注重点是在传输过程中保持通信的私密性，然而并无法保证数据在处理时或者到达用户设备时的安全性。这些协议也不会去管理群注册的安全性，WhatsApp最近发现的[漏洞](https://www.wired.com/story/whatsapp-security-flaws-encryption-group-chats/)就是典型案例。如果攻击者入侵了WhatsApp服务器，那么就可以在未经群管理员许可的情况下，将新成员加入群中。这意味着动机充足的攻击者可能会挑选并窃听特定的WhatsApp小组，从这个角度来讲该应用已无法保证所有通信数据的端到端加密。

[![](https://p3.ssl.qhimg.com/t013e1308c0d0083644.png)](https://p3.ssl.qhimg.com/t013e1308c0d0083644.png)

图1. Signal承诺保证用户消息安全（来源：[http://www.signal.org）](http://www.signal.org%EF%BC%89)

除这些应用的技术层面之外，背后的用户也是不容忽视的一面。

这些应用都声称自己关注安全及隐私，某些应用甚至还声称自己能“不受黑客攻击”。这些宣传语的目的都是让用户建立对应用的信任。用户信任应用会保护自己隐私数据的安全。

由于这些应用都声称拥有数百万活跃用户，因此很明显并非所有用户都经过网络安全教育。因此，许多用户不能完全理解这些应用某些配置可能带来的安全风险及限制。保护用户的隐私安全并非只需要停留在技术层面，也需要以可接受的方式向用户提供正确信息，使用户即便不是安全专家，也能了解决策风险。

[![](https://p5.ssl.qhimg.com/t018c069aee7d64c138.png)](https://p5.ssl.qhimg.com/t018c069aee7d64c138.png)

图2. Telegram广告声称其能保障用户消息安全免受黑客攻击（来源：[http://www.telegram.com](http://www.telegram.com/)）

这些应用还有另一个重要功能，即跨平台特性。所有应用都支持主流移动设备平台，也包含桌面版本。正常用户都会理所当然地认为所有平台上的安全级别都相同。所有应用的网站上也在暗示应用的安全性、隐私性在所有平台上都保持一致。

[![](https://p0.ssl.qhimg.com/t01613e4cd1350f1203.png)](https://p0.ssl.qhimg.com/t01613e4cd1350f1203.png)

图3. 网站提示用户可以在各种平台上使用应用（来源：[http://www.signal.org](https://www.signal.org/)）

然而安全功能的实现往往因具体平台而有所区别。有些平台上风险更多，并且这些风险也需要告知用户，因为用户通常会认为每个平台都能为他们提供相同级别的安全防护。



## 三、问题描述

这些主流应用的用户大多没有经过网络安全教育，这意味着用户会盲目信任这些应用能够保证其信息安全。显然，这种信任源自于应用对其自身服务的宣传方式。

2018年5月16日，Talos发表了关于[Telegrab](https://blog.talosintelligence.com/2018/05/telegrab.html)的一篇文章，介绍了可以劫持Telegram会话的恶意软件。原理非常简单：如果攻击者可以复制桌面用户的会话令牌（session token），那么就能劫持会话。除了本地存储的信息外，攻击者不需要其他任何信息。无论信息是否经过加密都不重要，只要复制这个信息，攻击者就能使用该新信息创建一个影子会话（shadow session）。

之后我们想继续研究这种技术能否适用于其他消息应用，事实证明我们测试的所有应用（Telegram、Signal以及WhatsApp）都受此方法影响。这些应用处理会话的方式有所不同，因此在某种程度上会影响这种攻击方法的效果。

在下文中，我们会描述我们研究的攻击场景，其中攻击者已经复制或者劫持了这些应用的会话。



## 四、应用分析

### <a class="reference-link" name="Telegram%EF%BC%9A%E6%A1%8C%E9%9D%A2%E4%BC%9A%E8%AF%9D%E5%8A%AB%E6%8C%81"></a>Telegram：桌面会话劫持

Telegram似乎是会话劫持（session hijacking）的最佳目标，攻击发生时用户并不会收到任何通知。受害者发送或者接收的消息以及图像也会原封不动传输至攻击者的会话。

[![](https://p0.ssl.qhimg.com/t01346c1dcc506d0555.png)](https://p0.ssl.qhimg.com/t01346c1dcc506d0555.png)

图4. Telegram桌面环境中存在2个会话

一旦攻击者使用窃取的会话信息启动Telegram桌面应用，用户不会收到关于新会话的任何通知。用户需要手动确认同时是否存在其他在用会话。用户需要转到设置页面才能发现该信息，这对普通用户来说并不容易。当该消息在Telegram上显示时，大多数用户也很难注意到消息内容。

### <a class="reference-link" name="Signal%EF%BC%9A%E6%A1%8C%E9%9D%A2%E4%BC%9A%E8%AF%9D%E5%8A%AB%E6%8C%81"></a>Signal：桌面会话劫持

Signal以竞争条件（race condition）的方式来处理会话劫持。当攻击者使用已窃取的会话信息启动应用时，两方应用都会竞争这一会话。因此，用户会在桌面应用上看到错误消息，但移动设备上看不到错误消息。

[![](https://p1.ssl.qhimg.com/t01d78576992aeb4856.png)](https://p1.ssl.qhimg.com/t01d78576992aeb4856.png)

图5. 在Mac上创建的会话适用于Windows系统（反之亦然）

然而，当受害者看到这些警告消息时，攻击者实际上已经可以访问尚未被删除的所有联系人和先前聊天新信息。

为了避免竞争条件，攻击者只需要简单删除会话信息即可。当用户启动应用时，会收到重新链接应用的一个请求。

这种情况对安全专家来说是一种红色警报，然而对普通用户而言，他们可能会认为这只是应用中的一个错误。

[![](https://p5.ssl.qhimg.com/t01472833a9e43ecc41.jpg)](https://p5.ssl.qhimg.com/t01472833a9e43ecc41.jpg)

图6. 同一台设备的两个会话

当用户创建第二个会话时，只有移动设备能看到该会话，并且默认情况下，两个会话都使用同一个名称。

因此，攻击者可以查看甚至仿冒受害者。攻击者发送的消息也会传到受害者的合法设备上，但攻击者可以在发送消息的同时删除这些消息，避免被用户发现。如果攻击者在仿冒过程中使用了“Disappearing messages”功能，那么受害者更难发现这种攻击行为。

### <a class="reference-link" name="WhatsApp%EF%BC%9A%E6%A1%8C%E9%9D%A2%E4%BC%9A%E8%AF%9D%E5%8A%AB%E6%8C%81"></a>WhatsApp：桌面会话劫持

WhatsApp是唯一实现了通知机制的一款应用。在正常操作下，如果攻击者使用已窃取的会话信息在桌面上打开第二个会话，那么受害者应该会收到一则警告消息，如下图所示：

[![](https://p5.ssl.qhimg.com/t01d3f63911736cabd8.png)](https://p5.ssl.qhimg.com/t01d3f63911736cabd8.png)

图7. WhatsApp多登录通知

当创建第二个会话时，在线的应用会收到这个通知消息。在用户做出决定之前，第二个会话处于有效并可用状态。因此，当出现此通知时，攻击者已经可以访问受害者的所有联系人消息及先前消息。攻击者也可以仿冒受害者，直到受害者对该窗口做出决断。假设攻击过程中受害者没有在设备旁，那么在受害者返回前攻击者一直都具备访问权限。如果受害者使用的是移动设备，那么他们并不会收到明显的警告信息。如果受害者使用的是桌面客户端，那么每次复用会话时都能看到这则通知。第二个会话不能修改警告。

这种告警机制仍存在缺陷，攻击者可以通过如下步骤绕过：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01895d9fffb53edf1e.png)

图8. 绕过WhatsApp多登录通知步骤

攻击者可以简化上述步骤，跳过步骤4，在执行步骤5之前静静等待。这样结果一样，因为双方都能访问相同的消息。只有当受害者在移动设备上手动终止会话，攻击者才会失去访问权限。

根据我们的协调披露政策，我们已经将漏洞反馈至Facebook，大家可以访问[此处](https://www.talosintelligence.com/vulnerability_reports/TALOS-2018-0643)了解所有公告详情。

### <a class="reference-link" name="Telegram%EF%BC%9A%E7%A7%BB%E5%8A%A8%E7%89%88%E5%BD%B1%E5%AD%90%E4%BC%9A%E8%AF%9D"></a>Telegram：移动版影子会话

不单单是桌面环境存在会话滥用问题，实际环境中已经有攻击者通过克隆的移动应用滥用这些会话。

[![](https://p0.ssl.qhimg.com/t0153354ae1c2cf8f75.png)](https://p0.ssl.qhimg.com/t0153354ae1c2cf8f75.png)

图9. 移动设备上的影子会话

在移动环境中，攻击者不必担心会话被入侵，在正常情况下攻击者很难获得会话数据。然而这里根本的问题在于，Telegram会根据同一个手机号码，允许同一台设备上存在影子会话（shadow session）。

这就存在一种攻击场景，在会话被终止前，攻击者可以读取Telegram中的所有消息以及联系人。在移动设备上，除非用户通过选项菜单请求终止会话，否则会话永远不会被终止。

Android平台上还有另一种攻击场景，恶意应用可以在无需用户交互的情况下创建影子会话。恶意应用只需获取“读取短信”和“结束后台进程”的权限即可，而这些权限请求行为通常不会被当成危险行为，可以轻松通过Google Play的审核。

Telegram注册过程首先会请求获取手机号码，然后通过包含唯一码的SMS确认手机号码有效。如果用户尝试再次注册同一个手机号码，Telegram会通过Telegram频道（而非SMS）发送一个验证代码。

将传输渠道从SMS切换成Telegram消息应当能够避免恶意应用在无需用户交互的情况下创建影子会话，因为恶意应用无法读取验证码。然而，如果注册过程无法在一定时间内顺利完成，Telegram就会假设用户无法访问Telegram应用，会通过SMS发送新的验证码。

这种备份机制造成了竞争条件，可以被恶意应用利用，在无需用户交互的情况下创建影子会话。整个操作过程如下：

[![](https://p4.ssl.qhimg.com/t018ff80ac27426bcc0.png)](https://p4.ssl.qhimg.com/t018ff80ac27426bcc0.png)

图10. 创建Telegram影子会话

从此时起，恶意应用就可以访问所有联系人、不属于“Secret chats”的以前以及未来消息。



## 五、总结

安全即时消息应用可以在消息传输过程中保证信息安全性，甚至可以保护这些消息不受应用服务器的影响。然而，在保护应用状态及用户消息方面，这些应用有点力不从心，会将信息保护责任交由操作系统来承担。

Signal协议开发者已经预见到会话劫持可能。会话管理协议（[Sesame](https://signal.org/docs/specifications/sesame/)协议）安全考虑中包含一个子章节，专门针对设备被入侵的情况，其中提到一句话：“如果攻击者成功获知设备的秘密数据，比如身份私钥以及会话状态，那么安全性将会受到灾难性影响”。

鉴于协议开发者已经预见到这种攻击方式，因此个人用户或者企业不应当认为这些应用固若金汤。因此，如果企业使用这些应用来传输私密或者敏感消息，那么他们应该部署能够更好保护这些资产的端点技术，这一点非常重要。
