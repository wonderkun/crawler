> 原文链接: https://www.anquanke.com//post/id/144765 


# Nigelthorn恶意软件滥用Chrome扩展,是怎么做到的?


                                阅读量   
                                **73197**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://blog.radware.com
                                <br>原文地址：[https://blog.radware.com/security/2018/05/nigelthorn-malware-abuses-chrome-extensions/](https://blog.radware.com/security/2018/05/nigelthorn-malware-abuses-chrome-extensions/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0121fb0f6fcbba9b9a.jpg)](https://p0.ssl.qhimg.com/t0121fb0f6fcbba9b9a.jpg)



## 写在前面的话

在2018年5月3日，Radware的恶意软件保护服务通过使用机器学习算法，在其全球制造公司之一的客户中发现了一个0day的恶意软件威胁。这款恶意软件在Facebook上传播的，通过滥用谷歌的Chrome扩展(Nigelify的应用程序)来感染用户，它会进行凭证盗窃，加密，点击欺诈等等。<br>
Radware威胁研究小组进一步调查显示，该组织自2018年3月起至今一直活跃，已经在100多个国家中感染了100,000多名用户。Facebook恶意软件活动并不新鲜。类似行动的例子包括facexworm和digimine，但由于一直在变化的应用程序和使用逃避机制散播恶意软件，这个组织似乎到目前为止还未被发现。

[![](https://p3.ssl.qhimg.com/t01f2e647a078e95ad7.png)](https://p3.ssl.qhimg.com/t01f2e647a078e95ad7.png)



## 感染过程

Radware将其称为恶意软件命名为“Nigelthorn”,因为Nigelify应用程序将图片替换为“Nigel Thornberry”。恶意软件将受害者重定向到一个虚假的YouTube页面，并要求用户安装Chrome扩展程序来播放视频。

[![](https://p0.ssl.qhimg.com/t010416768d363ae087.png)](https://p0.ssl.qhimg.com/t010416768d363ae087.png)

一旦用户点击“添加扩展”，恶意扩展就会被安装，机器就会成为僵尸网络的一部分。恶意软件依赖于Chrome并在Windows和Linux上运行。需要强调的是，该软件专注于Chrome浏览器，Radware相信不使用Chrome的用户不会面临风险。



## 僵尸网络统计

Radware收集了各种来源的统计数据，包括Chrome网上商店的恶意扩展统计数据和Bitly URL缩短服务。点击“添加扩展名”的受害者被重定向到一个Bitly网址，他们将被重定向到Facebook。这是为了诱骗用户并检索对其Facebook账户的访问。超过75％的感染来自菲律宾，委内瑞拉和厄瓜多尔。剩余的25％分布在其他97个国家。

[![](https://p2.ssl.qhimg.com/t0160e96b1834b9ce1e.png)](https://p2.ssl.qhimg.com/t0160e96b1834b9ce1e.png)



## 绕过Google应用程序验证工具

这个组织创建了一个合法扩展的副本并注入一个简短的混淆恶意脚本来启动恶意软件操作。

[![](https://p1.ssl.qhimg.com/t01f196e4ddf2d918cf.png)](https://p1.ssl.qhimg.com/t01f196e4ddf2d918cf.png)

Radware认为这样做是为了绕过谷歌的扩展验证。迄今为止，Radware的研究小组已经观察到七种这样的恶意扩展，其中四种已经被谷歌的安全算法识别和阻止。但Nigelify和PwnerLike仍然保持活跃。



## 已知的扩展

[![](https://p0.ssl.qhimg.com/t0149b1dd8987b756e6.png)](https://p0.ssl.qhimg.com/t0149b1dd8987b756e6.png)



## 恶意软件

一旦在Chrome浏览器上安装了扩展程序，就会执行从C2下载的恶意JavaScript初始配置（请参见下文）。

[![](https://p2.ssl.qhimg.com/t01facb29d4aee535c0.png)](https://p2.ssl.qhimg.com/t01facb29d4aee535c0.png)

随后将部署一组请求，每个请求都有自己的目的和触发器。以下是通信协议。

[![](https://p4.ssl.qhimg.com/t019b43aad5e749b86c.png)](https://p4.ssl.qhimg.com/t019b43aad5e749b86c.png)



## 恶意软件功能

### <a class="reference-link" name="%E6%95%B0%E6%8D%AE%E7%9B%97%E7%AA%83"></a>数据盗窃

恶意软件专注于窃取Facebook登录凭证和Instagram Cookie。如果机器上已经登录（或者找到一个Instagram cookie），它将被发送到C2。

[![](https://p4.ssl.qhimg.com/t01f3a074a4dd2831ad.png)](https://p4.ssl.qhimg.com/t01f3a074a4dd2831ad.png)

然后用户被重新定向到Facebook API来生成一个访问令，如果成功的话它也会被发送到C2 。

### <a class="reference-link" name="Facebook%E4%BC%A0%E6%92%AD"></a>Facebook传播

认证用户的Facebook访问令牌生成并且传播阶段开始。恶意软件收集相关的账户信息，目的是将恶意链接传播到用户的网络上。访问C2路径“/php3/doms.php”并返回随机URI。例如：

[![](https://p2.ssl.qhimg.com/t01a5995c3f2adc072c.png)](https://p2.ssl.qhimg.com/t01a5995c3f2adc072c.png)

这个链接有两种方式：通过Facebook Messenger发送消息，或者作为一个新帖子，其中包含最多50个联系人的标签。一旦受害者点击链接，感染流程就会重新开始并将其重定向到类似YouTube的网页，该网页需要“插件安装”才能查看视频。

### <a class="reference-link" name="Cryptomining"></a>Cryptomining

另一个下载的插件是一个加密工具。攻击者使用公开的浏览器挖矿工具来让受感染的机器开始挖掘加密货币。JavaScript代码是从组控件的外部站点下载的，并包含挖掘池。Radware观察到，在过去的几天里，该小组试图挖掘三种不同的硬币（Monero，Bytecoin和Electroneum），这些硬币都基于允许通过任何CPU进行采矿的“CryptoNight”算法。

`Radware的见证了池：`<br>`•supportxmr.com - 46uYXvbapq6USyzybSCQTHKqWrhjEk5XyLaA4RKhcgd3WNpHVXNxFFbXQYETJox6C5Qzu8yiaxeXkAaQVZEX2BdCKxThKWA`<br>`•eu.bytecoin-pool.org - 241yb51LFEuR4LVWXvLdFs4hGEuFXZEAY56RB11aS6LXXG1MEKAiW13J6xZd4NfiSyUg9rbERYpZ7NCk5rptBMFE5uZEinQ`<br>`•etn.nanopool.org - etnk7ivXzujEHf1qXYfNZiczo4ohA4Rz8Fv4Yfc8c5cU1SRYWHVry7Jfq6XnqP5EcL1LiehpE3UzD3MBfAxnJfvh3gksNp3suN`

在撰写本文时，约六千美元的开采时间大约是1,000美元，主要来自莫内罗池。

[![](https://p2.ssl.qhimg.com/t0179580adc870e6457.png)](https://p2.ssl.qhimg.com/t0179580adc870e6457.png)



## 持久性

恶意软件使用许多技术来保持机器的持久性，并确保其在Facebook上的活动持久。<br>
1.如果用户尝试打开扩展选项卡以删除扩展名，则恶意软件会将其关闭并阻止移除。

[![](https://p2.ssl.qhimg.com/t01f2b9b862056fba4d.png)](https://p2.ssl.qhimg.com/t01f2b9b862056fba4d.png)

2.恶意软件从C2下载URI Regex并阻止尝试访问这些模式的用户。以下链接展示了恶意软件如何防止访问Facebook和Chrome清理工具，甚至阻止用户进行编辑，删除帖子和发表评论。

`•https`<br>`:`<br>`//www.facebook.com/ajax/timeline/delete*•https://www.facebook.com/privacy/selector/update/*•https://www.facebook.com/react_composer/edit/ INIT / *`<br>`•https://www.facebook.com/composer/edit/share/dialog/*`<br>`•https://www.facebook.com/react_composer/logging/ods/*`<br>`•HTTPS：//www.facebook。 com / ajax / bz •https: //www.facebook.com/si/sentry/display_time_block_appeal/ ? type`<br>`= secure_account* •https:`<br>`//www.facebook.com/ajax/mercury/delete_messages.php*•https`<br>`：/ /www.facebook.com/ufi/edit/comment/*`<br>`•https://www.facebook.com/ufi/delete/comment/*`<br>`•https://www.facebook.com/checkpoint/flow*`<br>`•HTTPS： //dl.google.com/*/chrome_cleanup_tool.exe*`<br>`•https://www.facebook.com/security/*/download*`<br>`•https：//*.fbcdn.net/*.exe*`

### <a class="reference-link" name="YouTube%E6%AC%BA%E8%AF%88"></a>YouTube欺诈

一旦YouTube插件被下载并执行，恶意软件就会试图访问URI“/php3/ YouTube”。在C2上接收命令。检索到的指令可以是观看、喜欢或评论视频或订阅页面。Radware相信，该集团正试图从YouTube获得付款，但我们没有看到任何高浏览量的视频。来自C2的指令的一个例子:

``{``<br>`“result”：[`<br>``{`“id”：“5SSGxMAcp00”，`<br>`“type”：“watch”，`<br>`“name”：“Sanars  u0131n animasyon yap  u0131lm  u0131  u015f | “ANKARA”，`<br>`“time”：“07.05.2018 17:16:30”`}`，`<br>``{``<br>`“id”：“AuLgjMEMCzA”，`<br>`“start”：“47”，`<br>`“finish”： 1547，`<br>`“type”：“like”，`<br>`“name”：“DJI phantom 3 sahil”，`<br>`“time”：“07.05.2018 17:19:38”`<br>``}`，`<br>``{``<br>`“id”：“AuLgjMEMCzA”，`<br>`“type”： “watch”，`<br>`“name”：“DJI phantom 3 sahil”，`<br>`“time”：“07.05.2018 17:30:25”`<br>``}``<br>`]`<br>``}``



## 恶意软件保护

0day恶意软件利用复杂的逃避技术，这些技术常常绕过现有保护措施。尽管有多种安全解决方案，但Radware并未在一个保护良好的网络中发现Nigelify。Radware的机器学习算法分析了该组织的通信日志，将多个指标相关联，并阻止了受感染机器的C2访问。Radware的云恶意软件保护服务提供了多种功能。

•使用机器学习算法检测新的0day恶意软件<br>
•通过与现有的保护机制和防御层整合来阻止新的威胁<br>
•报告组织网络中恶意软件感染的企图<br>
•审核针对新漏洞利用和防御漏洞的防御措施

随着恶意软件的传播，组织将继续尝试寻找新的方法来利用被盗的资产。这些组织将会不断地制造新的恶意软件来绕过安全控制。Radware推荐个人和组织更新他们的密码，并且只从可信的来源下载应用程序。

[![](https://p2.ssl.qhimg.com/t01b78866860cca482b.png)](https://p2.ssl.qhimg.com/t01b78866860cca482b.png)



## 妥协指标

[![](https://p1.ssl.qhimg.com/t01bba6165e0473d39f.png)](https://p1.ssl.qhimg.com/t01bba6165e0473d39f.png)

这些浏览器扩展已经被报告给适当的一方，并且它们已被删除。


