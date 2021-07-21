> 原文链接: https://www.anquanke.com//post/id/164579 


# ATM攻击和场景分析（下）


                                阅读量   
                                **182994**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ptsecurity，文章来源：ptsecurity.com
                                <br>原文地址：[https://www.ptsecurity.com/upload/corporate/ww-en/analytics/ATM-Vulnerabilities-2018-eng.pdf](https://www.ptsecurity.com/upload/corporate/ww-en/analytics/ATM-Vulnerabilities-2018-eng.pdf)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01c664d81416400aae.jpg)](https://p0.ssl.qhimg.com/t01c664d81416400aae.jpg)



## Cash robbery

### <a name="Black%20Box"></a>Black Box

[![](https://p1.ssl.qhimg.com/t0119a34c35ba436649.png)](https://p1.ssl.qhimg.com/t0119a34c35ba436649.png)

前面提到过过，cash dispenser位于safe中，是有物理保护的。但cash dispenser与ATM计算机的连接位于safe之外，因此很容易就可以访问。有犯罪分子在ATM的前面板上挖洞来访问dispenser cable。这样，犯罪分子就可以直接连接到cash dispenser到他们自己的设备，他们的设备一般是一个运行修改过的ATM诊断工具的单片机，可以发送提现命令。一般来说，诊断工具会检查验证访问是不是合法的，但攻击者知道怎么样去绕过检查和其他安全机制。这些技术加起来就叫做lack Box攻击。

[![](https://p2.ssl.qhimg.com/t010f2ef23c4b40ebc8.png)](https://p2.ssl.qhimg.com/t010f2ef23c4b40ebc8.png)

图11. Black Box组件

[![](https://p3.ssl.qhimg.com/t01dcc694b01aad51d9.png)](https://p3.ssl.qhimg.com/t01dcc694b01aad51d9.png)

图12. A Black Box

[![](https://p4.ssl.qhimg.com/t01996e71991f07c58f.png)](https://p4.ssl.qhimg.com/t01996e71991f07c58f.png)

图13. A Black Box攻击

为了预防Black Box攻击，ATM厂商建议使用最新的XFS对OS和dispenser之间进行强加密和物理认证。如果有物理认证，加密密钥就只会在确认了对safe的合法访问后才会发送。但是攻击者也有一些应对的方式，比如墨西哥的犯罪分子在攻击者就用endoscope模拟了物理认证。而且在最新的软件版本中加密也没有很好的实现。2018年Positive Technologies就发现了可以在dispenser控制器上安装修改版的固件和绕过物理认证的方法。

而且有一半的ATM中使用的都是有漏洞的NCR保护系统。而且有19%的ATM一点点应对Black Box攻击的保护措施也没有。

### <a name="%E5%BB%BA%E8%AE%AE"></a>建议
1. 在OS和dispenser之间使用物理认证来确认对safe的合法访问；
1. 加密ATM OS和dispenser之间的数据；
1. 使用最新的软件版本，定期安装更新；
1. 监控和记录安全事件；
1. 考虑使用外部设备来保护对cash dispenser的非授权认证。


## 退出kiosk模式

一般的ATM用户只设计了与一个应用交互，这个应用就可以接收来自用户的输入并在屏幕上展示信息。应用运行在kiosk模式，也就是说用户不能运行其他程序或访问OS函数。如果推出kiosk模式，攻击者就可以绕过这些限制，在ATM OS中运行命令了。<br>
下面是几个潜在的攻击场景：

1.攻击者用一个设备来模拟用户键盘输入，并将该设备连接到ATM的USB或PS/2接口上。攻击的下一步就可以完全自动化，或远程完成。<br>
2.攻击者获取对OS的访问权限。在hotkey的帮助下推出kiosk模式，对输入的限制就没有了。<br>
3.最后一步是绕过应用控制（Application Control），获取发送命令到cash dispenser的能力。

[![](https://p3.ssl.qhimg.com/t011b84f5b00ebfcd80.png)](https://p3.ssl.qhimg.com/t011b84f5b00ebfcd80.png)

图14. 连接到攻击者设备

[![](https://p2.ssl.qhimg.com/t01fca1abc03615fd9f.png)](https://p2.ssl.qhimg.com/t01fca1abc03615fd9f.png)

图16.退出kiosk模式：攻击场景

### <a name="%E6%B5%8B%E8%AF%95%E4%B8%AD%E5%8F%91%E7%8E%B0%E7%9A%84%E6%BC%8F%E6%B4%9E"></a>测试中发现的漏洞

在对ATM的测试中研究人员发现的漏洞有配置错误，对用户权限限制不够，应用控制漏洞。

[![](https://p3.ssl.qhimg.com/t018e15055e9bef7afd.png)](https://p3.ssl.qhimg.com/t018e15055e9bef7afd.png)

图17. 漏洞分布

大多数测试的ATM都允许自由连接USB或PS/2设备。因此，犯罪分子可以连接键盘或其他模拟用户输入的设备。预防对任意信息的输入是非常重要的，比如特定的字符串组合可以推出kiosk模式，获取对OS函数的访问权限。大多数测试的ATM都运行着特殊的软件来有选择地禁用key组合。但85%的安理中，标准key组合仍然是可用的，包括Alt+F4，Win+Ctrl, Alt+Tab, Alt+Shift+Tab等。这些技术允许关闭STM kisok应用窗口，关闭负责拦截任意键盘输入的应用。

[![](https://p1.ssl.qhimg.com/t017d93bbff718ee8b0.png)](https://p1.ssl.qhimg.com/t017d93bbff718ee8b0.png)

图18.用键盘快捷方式退出kiosk模式

退出kiosk模式的漏洞可能也存在于安全软件中。比如有2个ATM运行着记录视频和监控安全事件的软件。应用窗口是隐藏的，但在测试期间，研究任意发现如果把鼠标的光标移到屏幕中间，隐藏的窗口就出现了。应用含有可用编辑文件的函数，这就可以访问Windows资源管理器，随后访问计算机上的其他软件，如Internet Explorer和FAR Manager。

[![](https://p0.ssl.qhimg.com/t019a4e7e56552c1c1b.png)](https://p0.ssl.qhimg.com/t019a4e7e56552c1c1b.png)

图19. 从智能软件退出kiosk模式

[![](https://p3.ssl.qhimg.com/t01582a32eff15089a3.png)](https://p3.ssl.qhimg.com/t01582a32eff15089a3.png)

图20. 从智能软件退出kiosk模式

同样应该配置本地安全策略来拒绝用户读写文件或启动任意程序。对大多数测试的ATM，本地安全策略一般都配置地不好或者完全没有。

测试的ATM中，有92%安装了应用控制解决方案。这都是为了预防恶意代码执行。应用控制配置的核心弱点在于如何创建白名单的应用，一般来说应用控制安装过程中系统中已有的软件都会被分类为可信的，但有些软件并不是ATM所必须的。因此，白名单软件的漏洞可能被攻击者利用来执行任意代码和关闭保护功能。

同时，研究任意还发现了ATM安全产品中的一些0 day漏洞，包括CVE-2018-13014, CVE-2018-13013, CVE-2018-13012等。

### <a name="%E5%BB%BA%E8%AE%AE"></a>建议

1.使用OS策略或设备控制解决方案来限制连接外部设备的能力；<br>
2.关闭可被用于获取OS函数访问权限的标准key组合；<br>
3.最小化权限，限制编辑文件、修改注册表、运行任意程序的能力；<br>
4.移除ATM正常功能非必须的软件，如果不能移除，使用安全工具来限制软件的功能；<br>
5.再次检查应用控制白名单：在构建白名单列表名单时，不包含非必须的OS服务和其他ATM运行所非必须的应用；<br>
6.强制执行对逻辑设备的排外访问，与厂商一起实现API变化和认证机制；<br>
7.使用最新版本的软件，定期安装更新；<br>
8.记录和监控安全事件。



## 连接硬盘

连接ATM硬盘后，就可能绕过安全机制并且获得cash dispenser的控制权。有以下可能的攻击场景：

[![](https://p3.ssl.qhimg.com/t01ab72b4986d6bfc22.png)](https://p3.ssl.qhimg.com/t01ab72b4986d6bfc22.png)

图21. 连接到ATM硬盘

### <a name="%E7%9B%B4%E8%BF%9E%E7%A1%AC%E7%9B%98"></a>直连硬盘

最简单的方法就是直接连接硬盘。如果硬盘没有加密，那么攻击者就可以复制一个含有取钱命令的恶意软件到硬盘中。然后攻击者可以简单修改一下配置文件将该程序加入应用控制白名单。如果随后ATM以secure模式重启，安全软件就会启动和工作，但攻击者仍然可以运行任意代码和恶意软件。攻击者可以完全关闭安全软件，比如从硬盘中删除文件。从硬盘复制敏感信息，然后修改用于之后的攻击。

### <a name="%E4%BB%8E%E5%A4%96%E9%83%A8%E7%A1%AC%E7%9B%98%E5%90%AF%E5%8A%A8"></a>从外部硬盘启动

攻击者可以从外部硬盘启动ATM来获取对文件系统的访问权限。启动顺序设置是在BIOS中设置的，对启动顺序的设置应该是密码保护的。但是有23%的ATM，BIOS密码很容易就可以猜到；还有8%的ATM都没有BIOS密码。在测试中，研究人员还发现可以在Intel Boot Agent的帮助下覆写BIOS启动顺序。

从另一个硬盘启动ATM，攻击者可以连接到原来的硬盘并实现前面提到的一些攻击场景。

[![](https://p1.ssl.qhimg.com/t01f82dcbfb6a2d7200.png)](https://p1.ssl.qhimg.com/t01f82dcbfb6a2d7200.png)

图22. 重命名McAfee Solidcore

[![](https://p1.ssl.qhimg.com/t014a16eff8a0a2684a.png)](https://p1.ssl.qhimg.com/t014a16eff8a0a2684a.png)

图23. 连接硬盘写入恶意软件

### <a name="%E6%B5%8B%E8%AF%95%E4%B8%AD%E5%8F%91%E7%8E%B0%E7%9A%84%E6%BC%8F%E6%B4%9E"></a>测试中发现的漏洞

允许访问硬盘文件系统的漏洞来源于BIOS访问认证的弱点和缺乏硬盘加密。因为对外部设备保护不佳，恶意软件可以与cash dispenser进行通信，尤其是OS和设备之间没有认证和加密的情况。

[![](https://p2.ssl.qhimg.com/t015dd453323a92f21d.png)](https://p2.ssl.qhimg.com/t015dd453323a92f21d.png)

图24. 漏洞分布

### <a name="%E5%BB%BA%E8%AE%AE"></a>建议

1.加密ATM硬盘。主要厂商NCR创建了加密最佳安全实践。其中包括如何在网络上传输加密密钥。<br>
2.对BIOS访问实施严格认证；<br>
3.使用UEFI而不是BIOS来确保加载内存完整性的控制；<br>
4.只允许从ATM硬盘启动，禁止通过外部硬盘或网络启动。



## 启动模式修改

以特殊模式启动ATM操作系统提供了一种绕过安全机制的方法。测试的ATM有一些启动模式：
1. Kernel debug mode
1. Directory Service Restore Mode
1. Safe modes (Safe Mode, Safe Mode with Networking, Safe Mode with Command Prompt)
在这些模式中，一些服务和保护机制是不能用的，也就有机会退出kiosk模式。在debug模式下启动ATM并连接到COM端口后，攻击者可以用winDbg工具获取ATM的完全控制权。设置了不同启动模式的ATM有大概88%，42%的ATM中测试人员发起了攻击并最终成功取现了。

[![](https://p4.ssl.qhimg.com/t0183d6da345901d6c9.png)](https://p4.ssl.qhimg.com/t0183d6da345901d6c9.png)

图25.修改启动模式

### <a name="%E5%BB%BA%E8%AE%AE"></a>建议

1.禁用从Windows loader选择启动模式的功能<br>
2.禁止通过COM/USB端口和网络来访问debug模式



## 卡数据窃取

银行卡磁条中含有执行交易所需的信息。虽然磁条有三个磁道，但一般都只用2个（Track1和 Track2）。Track1含有卡号、过期时间、服务码、所有者姓名。也可能含有PIN Verification Key Indicator, PIN Verification Value,和Card Verification Value。Track2有Track1中除所有者以外的所有信息。在POS机上刷磁条付款或从ATM上提现只需要读取Track2。所以攻击者会尝试从Track2拷贝信息。这些信息可以用于创建复制卡，用于在暗网出售。

过去这些年，有犯罪分子在读卡器上放了一个物理垫片来直接从磁条读取信息。银行注意到犯罪分子的这一行为，现在开始使用各种方式来预防物理垫片。但没有这种物理垫片也可以窃取信息，那就是使用拦截的方式。拦截一共分为2个阶段：
- ATM和处理中心进行数据传输时；
- ATM操作系统和读卡器进行数据传输时。
[![](https://p2.ssl.qhimg.com/t01af70f74067f1b78d.png)](https://p2.ssl.qhimg.com/t01af70f74067f1b78d.png)

图26. 针对卡数据窃取的攻击

### <a name="ATM%E5%92%8C%E5%A4%84%E7%90%86%E4%B8%AD%E5%BF%83%E4%B9%8B%E9%97%B4%E7%9A%84%E6%95%B0%E6%8D%AE%E6%8B%A6%E6%88%AA"></a>ATM和处理中心之间的数据拦截

因为Track2的所有值都是明文发送的，并且ATM和处理中心在应用级的流量没有加密，所以拦截是可能的。连接到ATM网络，并监听网络，攻击者就可以获取银行卡的相关信息。

[![](https://p0.ssl.qhimg.com/t01dea7d502727b76b9.png)](https://p0.ssl.qhimg.com/t01dea7d502727b76b9.png)

图27. 拦截明文的Track2信息

[![](https://p3.ssl.qhimg.com/t01ca8e23e31bede233.png)](https://p3.ssl.qhimg.com/t01ca8e23e31bede233.png)

图28. 拦截ATM和处理中心之间的数据

### <a name="%E6%8B%A6%E6%88%AA0S%E5%92%8C%E8%AF%BB%E5%8D%A1%E5%99%A8%E4%B9%8B%E9%97%B4%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88USB/com%E7%AB%AF%E5%8F%A3%EF%BC%89"></a>拦截0S和读卡器之间的数据（USB/com端口）

在ATM和读卡器之间放一个特殊的设备来拦截银行卡磁条的内容。因为与读卡器的通信也是没有认证和加密的，而且卡数据是以明文发送的，所以攻击也是可能实现的。研究发现在所有的测试ATM中都存在这样的问题。

### <a name="%E6%8B%A6%E6%88%AAOS%E5%92%8C%E8%AF%BB%E5%8D%A1%E5%99%A8%E4%B9%8B%E9%97%B4%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88%E6%81%B6%E6%84%8F%E8%BD%AF%E4%BB%B6%EF%BC%89"></a>拦截OS和读卡器之间的数据（恶意软件）

如果攻击者可以在ATM上安装恶意软件，那么读取卡数据就不需要恶意硬件了。安装恶意软件可以通过修改启动模式，从外部硬盘启动，直接连接到硬盘，执行网络攻击等多种方式执行。

在与读卡器进行数据交换时没有ATM会执行认证，因此所有的设备都可以访问。攻击者需要做的就是在ATM OS中运行任意代码。

[![](https://p2.ssl.qhimg.com/t0178168ef28fde8e9d.png)](https://p2.ssl.qhimg.com/t0178168ef28fde8e9d.png)

图29. 拦截读卡器和ATM OS之间的数据

### <a name="%E5%BB%BA%E8%AE%AE"></a>建议

1.加密与读卡器之间的数据交换。不要以明文发送Track2的所有内容。<br>
2.实现预防任意代码执行的建议。<br>
3.实现预防攻击ATM和处理中心的流量的网络攻击。



## 总结

逻辑攻击在ATM攻击中越来越常见，造成了数以百万美元计的损失。本文总结了ATM的工作原理以及两种针对ATM的攻击，以及若干攻击场景，并提出了预防攻击的建议。
