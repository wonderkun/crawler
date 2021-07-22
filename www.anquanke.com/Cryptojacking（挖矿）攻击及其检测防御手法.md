> 原文链接: https://www.anquanke.com//post/id/168114 


# Cryptojacking（挖矿）攻击及其检测防御手法


                                阅读量   
                                **360413**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者csoonline，文章来源：csoonline.com
                                <br>原文地址：[https://www.csoonline.com/article/3253572/internet/what-is-cryptojacking-how-to-prevent-detect-and-recover-from-it.html](https://www.csoonline.com/article/3253572/internet/what-is-cryptojacking-how-to-prevent-detect-and-recover-from-it.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0105f5da883bcecb19.jpg)](https://p0.ssl.qhimg.com/t0105f5da883bcecb19.jpg)

犯罪分子正在使用类似勒索软件的策略和中毒的网站，让你员工的计算机运行挖矿程序。本文将介绍关于cryptojacking攻击及其检测防御手法

## 一、什么是cryptojacking

Cryptojacking是未经授权使用其他人的计算机来挖掘**加密货币**[译者注：数字货币的一种]。黑客通过让受害者点击电子邮件中的恶意链接来加载计算机上的挖掘加密货币的代码，或者使用在受害者浏览器中加载后自动执行的JavaScript代码感染网站或在线广告来实现此目的。

无论是哪种方式，这些挖矿程序都会在后台运行。一点防范意识都没有的受害者除了可能可以发现电脑性能降低之外，什么都发现不了。



## 二、cryptojacking活动越发频繁

没有人清楚通过cryptojacking所产生的**加密货币**数量是多少，但毫无疑问cryptojacking十分疯狂。基于浏览器的cryptojacking行为次数增长迅速。去年11月，Adguard报告了浏览器内cryptojacking的增长率为31％。它的研究发现有33,000个网站运行挖矿脚本。据Adguard估计这些网站每月有10亿的访问量。

今年2月，Bad Packets报告发现了34,474个运行Coinhive的站点，Coinhive是最受欢迎的JavaScript挖掘器，也用于合法的加密挖掘活动。7月份，Check Point软件技术公司报告称，它发现的十大恶意软件中有四个是cryptojacking软件，包括排名前二的两个软件：Coinhive和Cryptoloot。

“**加密货币挖掘行业（挖矿）**正处于起步阶段。”网络安全解决方案提供商WatchGuard Technologies的威胁分析师Marc Laliberte表示，这里有很大的增长和发展空间。他指出，Coinhive易于部署，并在第一个月产生了30万美元。有利益的地方就有江湖，“从那时起，它发展十分迅速。这是一条赚钱的捷径。“

今年1月，研究人员发现了Smominru挖矿僵尸网络，该网络感染了超过50万台机器，这些机器主要分布在俄罗斯，印度和台湾。这次发现的僵尸网络主要针对Windows服务器进行Monero[译者注：门罗币]的开采，而据网络安全公司Proofpoint估计，截至1月底，它已经获利高达360万美元。

Cryptojacking实际上不需要用户了解很多重要的技术技能。据**The New Gold Rush Cryptocurrencies Are the New Frontier of Fraud**报道[译者注：[https://info.digitalshadows.com/TheNewGoldRush-CryptocurrencyResearch-Website.html，关于数字货币的一份报告]，一款在暗网上售卖的挖矿工具只需30美元就可以买到手。](https://info.digitalshadows.com/TheNewGoldRush-CryptocurrencyResearch-Website.html%EF%BC%8C%E5%85%B3%E4%BA%8E%E6%95%B0%E5%AD%97%E8%B4%A7%E5%B8%81%E7%9A%84%E4%B8%80%E4%BB%BD%E6%8A%A5%E5%91%8A%5D%EF%BC%8C%E4%B8%80%E6%AC%BE%E5%9C%A8%E6%9A%97%E7%BD%91%E4%B8%8A%E5%94%AE%E5%8D%96%E7%9A%84%E6%8C%96%E7%9F%BF%E5%B7%A5%E5%85%B7%E5%8F%AA%E9%9C%8030%E7%BE%8E%E5%85%83%E5%B0%B1%E5%8F%AF%E4%BB%A5%E4%B9%B0%E5%88%B0%E6%89%8B%E3%80%82)

因为Cryptojacking能够通过承担更少的风险来赚更多的钱，它正变得越来越受黑客欢迎。SecBI的首席技术官兼联合创始人Alex Vaystikh说：“黑客认为，与勒索软件相比，Cryptojacking成本更低并且可获利润更大”。因为，如果黑客使用勒索软件感染了100台计算机，他也许只能让其中的3个人为计算机付款。但相比之下，通过Cryptojacking，这100台受感染的计算机都可以源源不断的产生加密货币。

除此之外，Cryptojacking被发现的风险也远低于勒索软件。挖矿程序偷偷摸摸地在后台运行，并且很有可能长时间不被检测到。即使被发现，也很难追溯到源头，受害者没有驱动力去这样做，因为没有任何东西被盗或加密。黑客倾向于选择匿名加密货币，如Monero[译者注：门罗币]和Zcash[译者注：巴比特，首个使用零知识证明机制的区块链系统]，而不是更受欢迎的比特币，因为匿名加密货币很难被溯源。



## 三、cryptojacking的工作原理

黑客有两种主要方式让受害者的计算机偷偷挖掘加密货币。一种是欺骗受害者将加密代码加载到他们的计算机上。这是通过类似网络钓鱼的策略完成的：受害者收到一封看似合法的电子邮件，引诱他们去点击链接。然后链接运行代码在受害者的计算机上生成挖矿脚本。然后，当受害者使用它的计算机工作时，脚本会在后台运行。

另一种方法是在网站上注入脚本或将广告投放到多个网站。一旦受害者访问该网站或在其浏览器中弹出受感染的广告，该脚本将自动执行。在这种方法当中，挖矿脚本将不会存储到受害者的计算机上。无论使用哪种方法，挖矿脚本都会在受害者的计算机上计算复杂的数学问题，并将结果发送到黑客控制的服务器。

黑客通常会使用这两种方法来最大化他们的回报。Vaystikh说：“攻击者通过一些被植入挖矿代码的老版本的软件为受害者提供服务，从而获得回报” 举个栗子，在为黑客挖掘加密货币的100个设备中，10％可能通过受害者机器上的代码产生收入，而90％通过其Web浏览器获利。

与大多数其他类型的恶意软件不同，cryptojacking不会损坏计算机或受害者的数据。他们只是窃取了CPU处理资源。对于个人用户来说，运行速度较慢的计算机可能只是一个烦恼。对于拥有许多已被挖矿程序感染的系统的组织来说，挖矿程序会导致运维部门以及花在跟踪性能问题上的时间所需要的开销增大，只能期望通过更换系统和组件来解决问题。



## 四、真实的cryptojacking案例

Cryptojackers是聪明的人，他们已经设计了一些方案来让其他人的计算机挖矿。而这些方案大多数都不是新的：加密挖掘传递方法通常源自用于其他类型的恶意软件（如勒索软件或广告软件）的方法。Anomali安全策略主管Travis Farral说：“你可以看出来很多老方法，都是过去木马和勒索软件使用过的。现在他们不再使用勒索软件或特洛伊木马，而是保留软件的传播特性，重新修改软件的核心功能部分使其可以实现cryptojacking的功能。”

下面是一些现实中的例子

### <a class="reference-link" name="1.PowerGhost%EF%BC%9A%E9%80%9A%E8%BF%87Spear-fishing%E7%AA%83%E5%8F%96Windows%E5%87%AD%E6%8D%AE%E7%9A%84%E6%8C%96%E7%9F%BF%E7%A8%8B%E5%BA%8F"></a>1.PowerGhost：通过Spear-fishing窃取Windows凭据的挖矿程序

[译者注：Spear-fishing，鱼叉式网络钓鱼，是一种源于亚洲与东欧只针对特定目标进行攻击的网络钓鱼攻击]<br>
网络威胁联盟（CTA）的非法加密货币威胁报告描述了首先由Fortinet分析进行的PowerGhost。PowerGhost是一种可以通过多种方式避免检测的隐形恶意软件。它首先使用Spear-fishing在系统上获得立足点，然后它窃取Windows凭据并利用Windows Management Instrumentation（WMI）[译者注：可以通过WMI远程管理计算机，[https://docs.microsoft.com/zh-cn/windows/desktop/WmiSdk/about-wmi]和EternalBlue漏洞进行传播。然后它尝试禁用防病毒软件和其他挖矿程序](https://docs.microsoft.com/zh-cn/windows/desktop/WmiSdk/about-wmi%5D%E5%92%8CEternalBlue%E6%BC%8F%E6%B4%9E%E8%BF%9B%E8%A1%8C%E4%BC%A0%E6%92%AD%E3%80%82%E7%84%B6%E5%90%8E%E5%AE%83%E5%B0%9D%E8%AF%95%E7%A6%81%E7%94%A8%E9%98%B2%E7%97%85%E6%AF%92%E8%BD%AF%E4%BB%B6%E5%92%8C%E5%85%B6%E4%BB%96%E6%8C%96%E7%9F%BF%E7%A8%8B%E5%BA%8F)

### <a class="reference-link" name="2.%E5%8F%98%E7%A7%8DMinerGate%EF%BC%9A%E4%BC%9A%E5%9C%A8%E5%8F%97%E5%AE%B3%E8%80%85%E8%AE%A1%E7%AE%97%E6%9C%BA%E8%A2%AB%E4%BD%BF%E7%94%A8%E6%97%B6%E5%81%9C%E6%AD%A2%E6%8C%96%E7%9F%BF"></a>2.变种MinerGate：会在受害者计算机被使用时停止挖矿

根据CTA报告，Palo Alto Networks分析了MinerGate恶意软件系列的一个变种，并发现了一个有趣的功能。它可以检测鼠标移动并暂停采矿活动。这可以避免让受害者倾倒，避免他们注意到性能的下降。

### <a class="reference-link" name="3.BadShell%EF%BC%9A%E4%BD%BF%E7%94%A8Windows%E8%BF%9B%E7%A8%8B%E6%9D%A5%E5%AE%8C%E6%88%90%E5%85%B6%E6%8C%96%E7%9F%BF%E5%B7%A5%E4%BD%9C"></a>3.BadShell：使用Windows进程来完成其挖矿工作

几个月前，Comodo Cyber​​security在客户端系统上发现恶意软件，该系统使用合法的Windows进程来挖掘加密货币。它使用的是BadShell，具有以下特点
- 1.使用PowerShell执行命令，将恶意软件代码注入现有的运行进程。
- 2.使用计划任务来保证脚本的持久性
- 3.注册表保存恶意软件的二进制代码
### <a class="reference-link" name="4.%E5%86%85%E9%83%A8%E5%91%98%E5%B7%A5%E5%9C%A8%E5%85%AC%E5%8F%B8%E7%B3%BB%E7%BB%9F%E4%B8%8A%E8%BF%90%E8%A1%8C%E6%8C%96%E7%9F%BF%E7%A8%8B%E5%BA%8F"></a>4.内部员工在公司系统上运行挖矿程序

在今年早些时候的EmTech数字会议上，Darktrace讲述了一个客户，一家欧洲银行的故事，它在服务器上遇到了一些不寻常的流量模式。夜间流程运行缓慢，银行的诊断工具没有发现任何东西。Darktrace发现一个新的服务器在那段时间内上线，但该银行称该服务器不存在。对数据中心的实物检查表明，一名公司职员背地里使用该服务器运行挖矿程序

### <a class="reference-link" name="5.%E9%80%9A%E8%BF%87GitHub%E6%8F%90%E4%BE%9B%E6%8C%96%E7%9F%BF%E7%A8%8B%E5%BA%8F"></a>5.通过GitHub提供挖矿程序

今年3月，Avast Software报告称，加密攻击者正在使用GitHub作为托管恶意软件的主机。他们找到了合法的项目，他们从中创建了一个分叉项目。然后，恶意软件隐藏在该分叉项目的目录结构中。攻击者利用网络钓鱼攻击的方法，cryptojackers会引诱受害者下载该恶意软件。举个栗子，通过警告诱使他们进行点击某项内容从而下载恶意软件，比如：更新Flash播放器或者确定成人内容游戏网站的责任声明。

### <a class="reference-link" name="6.%E5%88%A9%E7%94%A8rTorrent%E6%BC%8F%E6%B4%9E"></a>6.利用rTorrent漏洞

Cryptojackers发现了一个rTorrent错误配置漏洞，该漏洞使得某些rTorrent客户端无需进行XML-RPC通信身份验证即可访问。他们在Internet上扫描暴露的客户端，然后在其上部署Monero cryptominer。安全服务提供商 F5 Networks在2月份报告了此漏洞，并建议rTorrent用户确保其客户不接受外部连接。

### <a class="reference-link" name="7.Facexworm%EF%BC%9A%E6%81%B6%E6%84%8FChrome%E6%89%A9%E5%B1%95%E7%A8%8B%E5%BA%8F"></a>7.Facexworm：恶意Chrome扩展程序

这种恶意软件是卡巴斯基实验室于2017年首次发现的，是一款谷歌Chrome扩展程序，它使用Facebook Messenger感染用户的计算机。最初，Facexworm提供了广告软件。今年早些时候，趋势科技发现了各种针对加密货币交换的Facexworm，并且能够提供挖矿代码。它仍然使用受感染的Facebook帐户来传递恶意链接，但也可以窃取网络帐户和凭据，这允许它将挖矿代码注入到这些网页当中。

### <a class="reference-link" name="8.WinstarNssmMiner%EF%BC%9A%E4%BC%9A%E9%80%A0%E6%88%90%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%B4%A9%E6%BA%83%E7%9A%84%E6%8C%96%E7%9F%BF%E7%A8%8B%E5%BA%8F"></a>8.WinstarNssmMiner：会造成计算机崩溃的挖矿程序

今年5月，360 Total Security发现了一个挖矿程序，它迅速传播并被证实来源于cryptojackers。这个恶意软件被称为WinstarNssmMiner，如果受害者尝试去删除它，那么它将导致受害者的计算机崩溃。WinstarNssmMiner通过首先启动svchost.exe进程并将代码注入其中并将生成的进程的属性设置为CriticalProcess来实现此目的。由于计算机被视为其中的一个关键过程，因此一旦删除该过程，计算机就会崩溃。

### <a class="reference-link" name="9.CoinMiner%EF%BC%9A%E6%94%BB%E5%87%BB%E5%85%B6%E4%BB%96%E6%8C%96%E7%9F%BF%E7%A8%8B%E5%BA%8F%E7%9A%84%E7%9F%BF%E7%8E%8B"></a>9.CoinMiner：攻击其他挖矿程序的矿王

Cryptojacking已经变得非常普遍，因此黑客设计他们的恶意软件，以便在他们感染的系统上查找并杀死已经运行的其他Cryptojacking。CoinMiner就是一个例子。<br>
根据Comodo的说法，CoinMiner会检查Windows系统上是否存在AMDDriver64进程。在CoinMiner恶意软件中有两个列表，$ malwares和$ malwares2，它们包含已知属于其他密码系统的进程的名称。然后它会杀死这些进程。



## 五、如何防止Cryptojacking

### <a class="reference-link" name="1.%E5%B0%86Cryptojacking%E6%94%BB%E5%87%BB%E5%A8%81%E8%83%81%E7%BA%B3%E5%85%A5%E5%AE%89%E5%85%A8%E5%9F%B9%E8%AE%AD%E5%BD%93%E4%B8%AD"></a>1.将Cryptojacking攻击威胁纳入安全培训当中

人是最关键的一环，重点关注通过网络钓鱼尝试将脚本加载到用户的计算机上的攻击手法。“当尝试通过技术去解决方案失败时，对人员的培训有利于保护自己。”Laliberte说。他认为网络钓鱼将继续成为传播所有类型恶意软件的主要方法。

### <a class="reference-link" name="2.%E5%9C%A8Web%E6%B5%8F%E8%A7%88%E5%99%A8%E4%B8%8A%E5%AE%89%E8%A3%85%E5%B9%BF%E5%91%8A%E6%8B%A6%E6%88%AA%E6%88%96%E5%8F%8D%E5%8A%A0%E5%AF%86%E6%89%A9%E5%B1%95"></a>2.在Web浏览器上安装广告拦截或反加密扩展

由于加密劫持脚本通常通过网络广告提供，因此安装广告拦截器可能是阻止它们的有效方法。Ad Blocker Plus等一些广告拦截器具有检测加密挖掘脚本的功能。Laliberte建议使用No Coin和MinerBlock等扩展，这些扩展旨在检测和阻止加密脚本。

### <a class="reference-link" name="3.%E4%BD%BF%E7%94%A8%E8%83%BD%E5%A4%9F%E6%A3%80%E6%B5%8B%E5%B7%B2%E7%9F%A5%E5%8A%A0%E5%AF%86%E7%9F%BF%E5%B7%A5%E7%9A%84%E7%AB%AF%E7%82%B9%E4%BF%9D%E6%8A%A4"></a>3.使用能够检测已知加密矿工的端点保护

许多端点保护/防病毒软件供应商已在其产品中添加了挖矿程序检测功能。“防病毒软件是在终端上试图防止挖矿程序的好东西之一。挖矿程序特征已知，那么它很有可能被检测到，”Farral说。他补充说，请注意，挖矿程序的作者不断改变他们的技术以避免程序被防病毒软件检测到。所以该方法存在一定滞后性

### <a class="reference-link" name="4.%E5%AE%89%E5%85%A8%E6%9C%8D%E5%8A%A1%E5%95%86%E7%9A%84Web%E8%BF%87%E6%BB%A4%E5%B7%A5%E5%85%B7%E5%BA%94%E8%AF%A5%E4%BF%9D%E6%8C%81%E6%9C%80%E6%96%B0"></a>4.安全服务商的Web过滤工具应该保持最新

如果安全服务商确定了一个提供挖矿程序的网页，它需要马上将其加入过滤名单中/过滤规则中

### <a class="reference-link" name="5.%E7%BB%B4%E6%8A%A4%E6%B5%8F%E8%A7%88%E5%99%A8%E6%89%A9%E5%B1%95"></a>5.维护浏览器扩展

一些攻击者正在使用恶意浏览器扩展或中毒合法扩展来执行加密挖掘脚本。

### <a class="reference-link" name="6.%E4%BD%BF%E7%94%A8%E7%A7%BB%E5%8A%A8%E8%AE%BE%E5%A4%87%E7%AE%A1%E7%90%86%EF%BC%88MDM%EF%BC%89%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88"></a>6.使用移动设备管理（MDM）解决方案

自带设备（BYOD）策略应对挖矿程序十分有效。“MDM可以在很大程度上保持BYOD的安全，”Laliberte说。MDM解决方案可以帮助管理用户设备上的应用和扩展。MDM解决方案倾向于面向大型企业，小型企业通常无力承担。但是，Laliberte指出，移动设备存在的风险比较小。因为它们往往具有较低的处理能力，所以黑客往往不会将移动设备作为首选攻击目标

因为以上的方法都不是万无一失的，并且Cryptojacking越来越猖獗，所以网络风险解决方案提供商Coalition嗅到了商机，对各大公司提供被诈骗保险。根据报道，它将偿还组织因欺诈性使用商业服务（包括加密采矿）而造成的直接财务损失。



## 六、如何检测Cryptojacking

就像勒索软件一样，尽管你尽最大努力阻止它，但加密劫持可能会影响你的组织。检测它可能很困难，特别是如果只有少数系统受到损害。不要依赖现有的端点保护工具来停止加密。“加密挖掘代码可以隐藏基于签名的检测工具，”Laliberte说。“桌面防病毒工具将无法看到它们。”以下是可行的：

### <a class="reference-link" name="1.%E5%AF%B9%E4%BD%A0%E7%9A%84%E8%BF%90%E7%BB%B4%E9%83%A8%E9%97%A8%E8%BF%9B%E8%A1%8C%E5%9F%B9%E8%AE%AD%EF%BC%8C%E8%AE%A9%E4%BB%96%E4%BB%AC%E5%AD%A6%E4%BC%9A%E5%A6%82%E4%BD%95%E5%AF%BB%E6%89%BE%E5%8A%A0%E5%AF%86%E9%87%87%E7%9F%BF%E7%9A%84%E8%BF%B9%E8%B1%A1%E3%80%82"></a>1.对你的运维部门进行培训，让他们学会如何寻找加密采矿的迹象。

SecBI的Vaystikh表示，有时挖矿程序的入侵第一个迹象应该是运维部门接到对计算机性能下降的投诉急剧增加。这应该引起极大的重视。<br>
Laliberte说，运维部门应该去寻找一些过热系统，这会导致CPU或冷却风扇故障。“由于CPU使用率过高导致损坏，可能会缩短设备的生命周期，”他说。平板电脑和智能手机等薄型移动设备尤其如此。

### <a class="reference-link" name="2.%E9%83%A8%E7%BD%B2%E7%BD%91%E7%BB%9C%E7%9B%91%E6%8E%A7%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88%E3%80%82"></a>2.部署网络监控解决方案。

Vaystikh认为，企业网络中的密码攻击比在家中更容易检测，因为大多数普通用户的终端解决方案都没有检测到它。但是对于企业来说，通过网络监控解决方案可以轻松检测到Cryptojacking，因为大多数企业组织都有网络监控工具。

但是，只有少数拥有网络监控工具和数据的组织拥有分析该信息以进行准确检测的工具和能力。例如，SecBI开发了一种人工智能解决方案，用于分析网络数据并检测加密劫持和其他特定威胁。

Laliberte同意网络监控是检测挖矿行为的最佳选择。“检查所有网络流量的网络边界监控有更好的机会检测挖矿程序，”他说。许多监控解决方案会将该活动向下钻取到各个用户，以便您可以识别受影响的设备。

“如果你在服务器上有一个良好的出口过滤，观察出站的流量，可以很好的检测出一些挖矿程序的运行，”Farral说。但他警告说，挖矿程序的作者可以通过修改他们的恶意软件来避免这种检测方法。

### <a class="reference-link" name="3.%E7%9B%91%E6%8E%A7%E6%82%A8%E8%87%AA%E5%B7%B1%E7%9A%84%E7%BD%91%E7%AB%99%E4%BB%A5%E8%8E%B7%E5%8F%96%E5%8A%A0%E5%AF%86%E6%8C%96%E6%8E%98%E4%BB%A3%E7%A0%81%E3%80%82"></a>3.监控您自己的网站以获取加密挖掘代码。

Farral警告说，Cryptojackers正在寻找在Web服务器上放置一些Javascript代码的方法。“服务器本身不是目标，但访问网站的任何人都具有被感染的风险，”他说。他建议定期监视Web服务器上的文件更改和页面更改情况

### <a class="reference-link" name="4.%E5%8F%8A%E6%97%B6%E4%BA%86%E8%A7%A3Cryptojacking%E8%B6%8B%E5%8A%BF%E3%80%82"></a>4.及时了解Cryptojacking趋势。

攻击方法和挖掘程序代码本身也在不断发展。Farral说，了解软件和行为可以帮助您检测加密。“一个聪明的组织应该时刻关注安全热点。”



## 七、如何处理已经遭受的Cryptojacking攻击

### <a class="reference-link" name="1.%E5%88%A0%E9%99%A4%E5%B9%B6%E9%98%BB%E6%AD%A2%E7%9B%B8%E5%85%B3%E7%BD%91%E7%AB%99%E6%8F%90%E4%BE%9B%E7%9A%84%E8%84%9A%E6%9C%AC"></a>1.删除并阻止相关网站提供的脚本

对于浏览器内JavaScript攻击，一旦检测到Cryptojacking，解决方案就很简单：关闭运行脚本的浏览器选项卡。安全服务公司应该关注脚本来源url，并更新公司的Web过滤器特征库。同时，也可以考虑部署反加密挖掘工具以帮助防止未来的攻击。

### <a class="reference-link" name="2.%E6%9B%B4%E6%96%B0%E5%92%8C%E6%B8%85%E9%99%A4%E6%B5%8F%E8%A7%88%E5%99%A8%E6%89%A9%E5%B1%95%E3%80%82"></a>2.更新和清除浏览器扩展。

更新所有扩展并删除那些不需要或被感染的扩展

### <a class="reference-link" name="3.%E5%AD%A6%E4%B9%A0%E5%92%8C%E9%80%82%E5%BA%94%E3%80%82"></a>3.学习和适应。

利用这些遭受攻击的经验可以更好地了解攻击者如何破坏您的系统。更新安全意识培训内容，以便用户，运维部门能够更好地识别Cryptojacking攻击并做出相应的响应。
