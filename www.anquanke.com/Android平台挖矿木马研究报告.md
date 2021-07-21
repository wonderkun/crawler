> 原文链接: https://www.anquanke.com//post/id/96028 


# Android平台挖矿木马研究报告


                                阅读量   
                                **352224**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    





[![](https://p2.ssl.qhimg.com/t018875b66aa8eed66b.jpg)](https://p2.ssl.qhimg.com/t018875b66aa8eed66b.jpg)

## 摘要
- 手机挖矿木马就是在用户不知情的情况下利用其手机的计算能力来为攻击者获取电子加密货币的应用程序。
- 电子加密货币是一种匿名性的虚拟货币，由于不受政府控制、相对匿名、难以追踪的特性，电子加密货币常被用来进行非法交易，也成为犯罪工具、或隐匿犯罪所得的工具。
- 2014年3月首个Android平台挖矿木马被曝光。
- 从2013年开始至2018年1月，360烽火实验室共捕获Android平台挖矿木马1200余个，其中仅2018年1月Android平台挖矿木马接近400个。
- 从Android平台挖矿木马伪装应用类型看，工具类（20%）、下载器类（17%）、壁纸类（14%）是最常伪装的应用类型。
- 从样本来源来看，除了被曝光的在Google play中发现的十多个挖矿木马外，我们在第三方下载站点捕获了300多个挖矿木马，总下载次数高达260万余次。
- 从网站来看，据Adguard数据显示，2017年近1个月时间内在Alexa排行前十万的网站上，约有220多个网站在用户打开主页时无告知的利用用户计算机进行挖矿，影响人数多达5亿。大多是以视频门户网站，文件分享站，色情网站和新闻媒体站等这类相对访问时间较长的站点。
- Android平台发现的挖矿木马选择的币种主要有（BitCoin）、莱特币(Litecoin)、狗币(Dogecoin)、卡斯币(Casinocoin) 以及门罗币（Monero）这五种。
- 挖矿方式有单独挖矿和矿池挖矿两种，Android平台挖矿木马主要采用矿池挖矿。
- Android平台挖矿木马技术原理从代码上看，主要分为使用开源的矿池代码库进行挖矿和使用浏览器JavaScript脚本挖矿。
- 挖矿木马的技术手段包括检测设备电量、唤醒状态、充电状态、设置不可见页面以及仿冒应用下载器。
- 应用盈利模式由广告转向挖矿，门罗币成为挖矿币种首选以及攻击目标向电子货币钱包转移成为Android平台挖矿木马的趋势。
- 目前挖矿木马的防御措施，PC平台已经具备防御能力，移动平台由于权限控制不能彻底防御。
- 移动平台挖矿受限于电池容量和处理器能力，但电子加密货币正在快速增长，现有货币增值并出现新的货币币种，挖矿最终会变得更有利可图。
- 国外这种全新的盈利模式，还处在起步阶段，还需要更多的控制和监管，避免被恶意利用。
**关键词：**手机挖矿木马、电子货币





## Android平台挖矿木马介绍
<li>
<h3 name="h3-2" id="h3-2">
<a name="_Toc504402178"></a><a name="_Toc503962398"></a> 什么是手机挖矿木马</h3>
</li>
挖矿（Mining），是获取[比特币](https://zh.wikipedia.org/wiki/%E6%AF%94%E7%89%B9%E5%B8%81)等电子加密货币的勘探方式的昵称。由于其工作原理与开采[矿物](https://zh.wikipedia.org/wiki/%E7%A4%A6%E7%89%A9)十分相似，因而得名。

手机挖矿木马就是在用户不知情的情况下利用其手机的计算能力来为攻击者获取电子加密货币的应用程序。
<li>
<h3 name="h3-3" id="h3-3">
<a name="_Toc504402179"></a><a name="_Toc503962399"></a> 电子加密货币</h3>
</li>
电子加密货币是一种匿名性的虚拟货币。它不依靠任何法定货币机构发行，更不受央行管控。交易在全球网络中运行，有特殊的隐秘性，加上不必经过第三方金融机构，因此得到越来越广泛的应用。

由于不受政府控制、相对匿名、难以追踪的特性，电子加密货币常被用来进行非法交易，也成为犯罪工具、或隐匿犯罪所得的工具。以WannaCry为代表的勒索软件，都采用比特币为支付工具。

2009年，[比特币](https://zh.wikipedia.org/wiki/%E6%AF%94%E7%89%B9%E5%B8%81)成为第一个[去中心化](https://zh.wikipedia.org/wiki/%E5%8E%BB%E4%B8%AD%E5%BF%83%E5%8C%96)的电子加密货币，也是目前知名度与[市场总值](https://zh.wikipedia.org/wiki/%E5%B8%82%E5%A0%B4%E7%B8%BD%E5%80%BC)最高的加密货币。

[![](https://p2.ssl.qhimg.com/t01ed83b6d4c5d33f8b.png)](https://p2.ssl.qhimg.com/t01ed83b6d4c5d33f8b.png)

比特币在2013年4月~2018年1月价格变化趋势[1]

2017年比特币的价格上涨了1500%，最高时单个比特币价格逼近2万美元。且随着比特币价格的疯狂上涨，挖矿木马的攻击事件也越来越频繁。
<li>
<h3 name="h3-4" id="h3-4">
<a name="_Toc504402180"></a><a name="_Toc503962400"></a> 手机挖矿木马历史演变</h3>
</li>
挖矿木马最早是2013年在PC平台上被发现，而首个手机挖矿木马CoinKrypt[2]最早被国外安全厂商在2014年3月曝光。手机挖矿木马经过一阵沉寂后，随着电子加密货币价格的一路走高，恶意软件作者又重新将目标转向了挖矿。手机挖矿木马的攻击事件也重回视野，且势必是未来恶意软件的趋势之一。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e5461e8c462b12a5.png)

2014年03月Android.Coinkrypt，Android平台上首个挖矿木马。

2014年04月Android. BadLepricon[3]，在Google Play上发现手机挖矿木马。

2014年05月Android. Widdit[4]，首个使用Android挖矿SDK的挖矿木马。

2017年10月Android.JsMiner[5]，首个加载JavaScript的挖矿木马。

2017年10月Android.CpuMiner[6]，首个使用cpuminer库的挖矿木马。

2017年12月Android.PickBitPocket[7]，伪装成比特币钱包的欺诈程序。

2017年12月Android.Loapi[8]，拥有复杂模块化架构的挖矿木马。

2018年1月Android.Hackword[9]，首个使用Coinhive安卓SDK挖矿的木马。


<li>
<h2 name="h2-5" id="h2-5"> Android平台挖矿木马现状</h2>
</li>
<li>
<h3 name="h3-6" id="h3-6">
<a name="_Toc504402182"></a><a name="_Toc503962402"></a> 规模和影响</h3>
</li>
从2013年开始至2018年1月，360烽火实验室共捕获Android平台挖矿木马1200余个，其中仅2018年1月Android平台挖矿木马接近400个，占全部Android平台挖矿类木马近三分之一。

2014年Android挖矿木马经过短暂的爆发后，于2015，2016年逐渐归于平静。主要原因是受到当时移动平台技术等限制，以及电子货币价格影响，木马作者的投入和产出比不高。但随着2017年年底电子货币价格的一路高涨，挖矿技术的成熟，再次得到木马作者的目标，手机挖矿木马在也呈爆发式增长。

[![](https://p1.ssl.qhimg.com/t0149f0730d096054b1.jpg)](https://p1.ssl.qhimg.com/t0149f0730d096054b1.jpg)

Android平台挖矿木马伪装成各类应用软件，统计发现其中工具类（20%）、下载器类（17%）、壁纸类（14%）是最常伪装的应用类型。

[![](https://p2.ssl.qhimg.com/t018e967f99ba0fe39d.png)](https://p2.ssl.qhimg.com/t018e967f99ba0fe39d.png)

从样本来源来看，除了被曝光的在Google play中发现的十多个挖矿木马外，我们在第三方下载站点捕获了300多个挖矿木马，根据其网页上的标识，估算出这个网站上的APP总下载次数高达260万余次。

[![](https://p3.ssl.qhimg.com/t01557aab932c8c9db3.jpg)](https://p3.ssl.qhimg.com/t01557aab932c8c9db3.jpg)

第三方下载站点下的挖矿木马

从网站来看，据Adguard数据显示[10]， 2017年近1个月内在Alexa排行前十万的网站上，约有220多个网站在用户打开主页时无告知的利用用户计算机进行挖矿，影响人数多达5亿。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ad9ae66ce170f0a8.jpg)

Adguard近一个月的调查数据

这些网站来自美国、印度、俄罗斯、中国、巴西以及中国等多个国家。

[![](https://p4.ssl.qhimg.com/t01181d0d9b9391ef76.jpg)](https://p4.ssl.qhimg.com/t01181d0d9b9391ef76.jpg)

主要国家占比

而这部分网站大多是以视频门户网站，文件分享站，色情网站和新闻媒体站等这类相对访问时间较长的站点。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01bcda56ad77c279b3.jpg)

挖矿网站分类情况
<li>
<h3 name="h3-7" id="h3-7">
<a name="_Toc504402183"></a><a name="_Toc503962404"></a> 目标币种</h3>
</li>
挖矿木马在币种选择上是随着币种的挖掘难度和币种相对价格等因素而变化。目前在Android平台发现的挖矿木马选择的币种主要有（BitCoin）、莱特币(Litecoin)、狗币(Dogecoin)、卡斯币(Casinocoin) 以及门罗币（Monero）这五种。

[![](https://p4.ssl.qhimg.com/t01ab44efd98b3c26ea.png)](https://p4.ssl.qhimg.com/t01ab44efd98b3c26ea.png)

币种优劣势对比
<li>
<h3 name="h3-8" id="h3-8">
<a name="_Toc504402184"></a><a name="_Toc503962405"></a> 挖矿方式及收益分配</h3>
</li>
挖矿方式有单独挖矿和矿池挖矿两种。下面以比特币为例来说明两种挖矿方式的区别。
<li>
<h4>
<a name="_Toc504402185"></a><a name="_Toc503962406"></a> 独立挖矿</h4>
</li>
独立挖矿是指使用自己计算机当前拥有的计算能力去参与比特币的挖掘，获取到的新区块的收益全归个人所有。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0100017e6b2f0b4f44.png)

独立挖矿流程

比特币平均每十分钟产生一个区块，而参与比特币挖掘的用户数量非常庞大，独立挖矿可能一整年也无法抢到一个区块。且手机的计算能力相比于其他挖矿设备更是有限，当前Android平台还未发现使用独立挖矿手段来获取电子货币的挖矿木马。
<li>
<h4>
<a name="_Toc504402186"></a><a name="_Toc503962407"></a> 矿池挖矿</h4>
</li>
矿工是参与[比特币勘探竞争的网络](https://zh.wikipedia.org/w/index.php?title=%E6%AF%94%E7%89%B9%E5%B8%81%E7%BD%91%E7%BB%9C&amp;action=edit&amp;redlink=1)成员的昵称。而矿池是一个通过特定算法而设计的服务器，所有连接到矿池服务器的用户，会组队进行挖矿。

个人设备的性能虽然渺小，但是成千上万的人进行组队挖矿，总体性能就会变得十分强大，在这种情况，挖矿的成功率会大大提升，一旦矿池中的队伍成功制造了一个区块，那么所有队伍中的人会根据每个人贡献的计算能力进行分红。矿池的开发者一般会对每个用户收取一定手续费，但由于这种方法让大家更稳定得获得比特币，大部分矿工都会选择矿池挖矿，而不是单独挖矿。

[![](https://p4.ssl.qhimg.com/t01e8d0b490877497a3.png)](https://p4.ssl.qhimg.com/t01e8d0b490877497a3.png)

矿池挖矿流程

矿池挖矿也分为一般矿池挖矿和前端矿池挖矿。
1. 一般矿池挖矿：
一般矿池挖矿直接利用CPU或GPU本身的高速浮点计算能力进行挖矿工作。由使用C或者其他语言构造的挖矿程序进行CPU或GPU计算得到算力价值。矿池根据产生的算力价值进行分红，并收取10%以下的矿池手续费。
1. 前端矿池挖矿：
前端挖矿利用asm.js或webAssembly前端解析器中介在浏览器端被动使用用户的CPU完成挖矿或者利用Html5新规范WebGL利用浏览器完成GPU挖矿操作。由浏览者产生的CPU或GPU计算得到算力价值。前端矿池（如Coinhive[11]）会收取30%的矿池手续费。

由于使用方便，跨平台且隐藏性较好等特点，前端矿池挖矿逐渐得到挖矿木马作者的青睐。<a name="_Toc503962408"></a>


<li>
<h2 name="h2-9" id="h2-9"> Android平台挖矿木马技术原理</h2>
</li>
<li>
<h3 name="h3-10" id="h3-10">
<a name="_Toc504402188"></a><a name="_Toc503962409"></a> 挖矿技术原理</h3>
</li>
在Android平台上攻击者为追求稳定的收益，挖矿方式通常都选择使用矿池来进行挖矿。攻击者通过挖矿木马远程控制用户手机，在用户不知情的情况下，使手机持续在后台挖掘电子货币来为其牟利。

[![](https://p1.ssl.qhimg.com/t0146fe3db8813ca5b3.png)](https://p1.ssl.qhimg.com/t0146fe3db8813ca5b3.png)

攻击者通过挖矿木马赚取收益的攻击流程

而在代码层上的表现形式为，嵌入开源的矿池代码库进行挖矿和使用矿池提供的浏览器JavaScript脚本进行挖矿。
<li>
<h4>
<a name="_Toc504402189"></a><a name="_Toc503962410"></a> 使用开源的矿池代码库进行挖矿</h4>
</li>
挖矿木马CpuMiner 使用开源的挖矿项目cpuminer来开采比特币和莱特币：

[![](https://p4.ssl.qhimg.com/t0157f2c07a4e0e1f4c.png)](https://p4.ssl.qhimg.com/t0157f2c07a4e0e1f4c.png)

Github开源项目

步骤一：注册的挖矿的广播和服务等组件，在Android Manifest里注册广播和挖矿的服务MiningService。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012d7678c645c46ef1.png)

步骤二：嵌入核心的挖矿的库文件

[![](https://p4.ssl.qhimg.com/t01204fe84e74188628.png)](https://p4.ssl.qhimg.com/t01204fe84e74188628.png)

步骤三：设置挖矿包括算法、矿池地址、矿工账户信息等基本信息开始挖矿。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01db66bc7ccd06eeba.png)

**步骤四：执行**cpuminer进行挖矿开始挖矿

[![](https://p3.ssl.qhimg.com/t014c7952d0c18f462c.png)](https://p3.ssl.qhimg.com/t014c7952d0c18f462c.png)
<li>
<h4>
<a name="_Toc504402190"></a><a name="_Toc503962411"></a> 使用浏览器JavaScript脚本挖矿</h4>
</li>
2017年9月，国外著名的BT站点Pirate Bay（海盗湾）[12]尝试在网页中植入JavaScript挖矿脚本，但由于兼容性问题，部分用户的CPU出现了100%的疯狂占用，官方承认他们有意借此来增加部分营收。

由于浏览器JavaScript挖矿脚本配置灵活简单，具有全平台化等特点，受到越来越多的恶意挖矿木马的青睐，同时也导致了利用JavaScript脚本挖矿的安全事件愈发频繁。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cf959715ea8bfcf2.png)

通过Coinhive提供的JavaScript API
<li>
<h3 name="h3-11" id="h3-11">
<a name="_Toc504402191"></a><a name="_Toc503962412"></a> 挖矿木马的技术手段</h3>
</li>
挖矿的过程运行会占用CPU或GPU资源，造成手机卡顿、发热或电量骤降等现象，容易被用户感知。为了隐匿自身挖矿的行为，挖矿木马会通过一些技术手段来隐藏或控制挖矿行为。
<li>
<h4>
<a name="_Toc504402192"></a><a name="_Toc503962413"></a> 检测设备电量</h4>
</li>
挖矿木马运行会导致电池电量明显下降，为保证手机在多数情况下正常运行而不被用户察觉，会选择在电池电量高于50%时才运行挖矿的代码。

[![](https://p5.ssl.qhimg.com/t0151325e3cfcf131d6.png)](https://p5.ssl.qhimg.com/t0151325e3cfcf131d6.png)

检测设备当前的电量是否大于50%
<li>
<h4>
<a name="_Toc504402193"></a><a name="_Toc503962414"></a> 检测设备唤醒状态</h4>
</li>
挖矿木马会检查手机屏幕的唤醒状态，当手机处于唤醒状态，当处于锁屏状态时才会开始执行，避免用户在与手机交互时感知到挖矿带来的卡顿等影响。

[![](https://p5.ssl.qhimg.com/t019d94e185e0bc0961.png)](https://p5.ssl.qhimg.com/t019d94e185e0bc0961.png)

检测屏幕唤醒状态
<li>
<h4>
<a name="_Toc504402194"></a><a name="_Toc503962415"></a> 检测设备充电状态</h4>
</li>
设备在充电时会有足够的电量和发热的想象。在充电时运行挖矿木马避免用户察觉挖矿带来的电量下降和发热等现象。

[![](https://p5.ssl.qhimg.com/t011423a16a2dd56e68.png)](https://p5.ssl.qhimg.com/t011423a16a2dd56e68.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c59258089600feb1.png)

通过MiningService服务连接Pickaxe矿池来挖掘比特币
<li>
<h4>
<a name="_Toc504402195"></a><a name="_Toc503962417"></a> 设置不可见的页面进行挖矿</h4>
</li>
挖矿木马通过设置android:visibility为invisible属性，达到不可见的Webview页面加载效果从而使用JavaScript脚本进行挖矿，隐藏自身的恶行挖矿行为。

[![](https://p1.ssl.qhimg.com/t0175b734577c27f408.png)](https://p1.ssl.qhimg.com/t0175b734577c27f408.png)

设置不可见的webview页面




<li>
<h4>
<a name="_Toc503962418"></a><a name="_Toc504402196"></a> 仿冒应用下载器</h4>
</li>
挖矿木马通过仿冒热门应用骗取用户下载，实际只是应用的下载器，软件启动后就开始执行挖矿，仅仅是提供了一个应用的下载链接。

[![](https://p2.ssl.qhimg.com/t01562a6f213bc78211.png)](https://p2.ssl.qhimg.com/t01562a6f213bc78211.png)

仿冒应用下载器


<li>
<h2 name="h2-12" id="h2-12"> Android平台挖矿木马趋势</h2>
</li>
Android平台挖矿木马的演变很大程度上受到PC上的挖矿木马影响，通过持续关注挖矿木马的攻击事件，我们发现Android平台挖矿木马正朝着三个方向发展。
<li>
<h3 name="h3-13" id="h3-13">
<a name="_Toc504402198"></a> 应用盈利模式由广告转向挖矿</h3>
</li>
通过分析来自某个APP下载网站的样本发现，在其早期的应用中内嵌了广告插件，软件运行时会联网来控制样本请求访问的广告，而在近期当软件访问同一个请求时，返回的内容加入Coinhive挖取门罗币的JS脚本。

[![](https://p2.ssl.qhimg.com/t014c1059e3874dcb2a.png)](https://p2.ssl.qhimg.com/t014c1059e3874dcb2a.png)

访问同一链接早期与近期返回内容对比

对该下载网站进行分析后，发现网站上的软件中都包含了Coinhive提供的Android SDK example。

[![](https://p1.ssl.qhimg.com/t012a1165149d283b79.png)](https://p1.ssl.qhimg.com/t012a1165149d283b79.png)
<li style="text-align: left;">
<h3 name="h3-14" id="h3-14">
<a name="_Toc504402199"></a><a name="_Toc503962423"></a> 门罗币成为挖矿币种首选</h3>
</li>
对于攻击者而言，选择现阶段币种价格相对较高且运算力要求适中的数字货币是其短期内获得较大收益的保障。

早期挖矿木马以比特币（BitCoin）、莱特币(Litecoin)、狗币(Dogecoin)、以及卡斯币(Casinocoin)为主。

而随着比特币挖矿难度的提高，新型币种不断出现，比特币已经不在是挖矿木马唯一的选择。门罗币（Monero）首发于2014年4月，发行时间相对较短，现阶段的挖矿木马主要以门罗币作为挖掘目标，主要在于门罗币相对其他电子加密货币拥有多种明显的优势：
- 门罗币具有更好的匿名性。门罗币在交易中，不涉及提供钱包地址。对方通过钱包地址来查看你的钱包资产情况。
- 门罗币有更好的挖矿算法。它并不依赖于ASIC，使用任何CPU或GPU都可以完成，这就意味着即使普通的计算机用户也能够参与到门罗币挖矿中来。甚至可以利用剩余的计算机能力来挖矿
- 门罗币拥有“自适应区块大小限制”。门罗币从一开始就设置了自适应的区块大小，这意味着，它可以自动的根据交易量的多少来计算需要多大的区块。因此门罗币从设计上就不存在像比特币的扩容等问题。
- 门罗币背后的研发团队的设计质量发展目标都很优越。互联网上有许多优秀的开源门罗币挖矿项目，拥有众多贡献者。
<li>
<h3 name="h3-15" id="h3-15">
<a name="_Toc504402200"></a><a name="_Toc503962424"></a> 黑客攻击目标向电子货币钱包转移</h3>
</li>
由于攻击电子货币钱包能直接获取大量的收益，PC上已出现多起攻击电子货币钱包的木马，通过盗取电子货币私钥或者在付款时更改账户地址等手段实现盗取他人账户下的电子货币。

[![](https://p1.ssl.qhimg.com/t01f49720cf1f9e7901.png)](https://p1.ssl.qhimg.com/t01f49720cf1f9e7901.png)

伪装成比特币钱包的PickBitPocket木马

而在Android平台也发现了类似的攻击事件，PickBitPocket木马伪装成比特币钱包应用，且成功上架在Google Play。其在用户付款时将付款地址替换成攻击者的比特币地址，以此来盗取用户账户下的比特币。

对于电子货币钱包应用本身存在的漏洞和风险，并没有引起足够的重视程度。比特币地址相当于银行帐号，私钥相当于开启这个帐号的密码。且通过私钥可以得知其比特币地址，并能对该地址下的比特币进行转账，也就是说获得比特币私钥就拥有了该私钥和地址下的比特币的完全控制权。我们在调查分析中发现部分电子货币钱包甚至将私钥未加密的备份在SD卡，对于私钥的备份、存储安全，还需要进一步的增强。<a name="_Toc503962425"></a>


<li>
<h2 name="h2-16" id="h2-16"> 挖矿木马的防御措施</h2>
</li>
<li>
<h3 name="h3-17" id="h3-17">
<a name="_Toc504402202"></a><a name="_Toc503962426"></a> 基于PC平台的防御策略</h3>
</li>
针对挖矿木马肆虐现状，360安全卫士和360安全浏览器率先推出“挖矿木马防护”功能，用户只要开启该功能，就能全面防御从各种渠道入侵的挖矿攻击。浏览网页时，会像屏蔽广告一样，自动为用户屏蔽挖矿脚本;下载及使用软件程序时，会实时拦截各类挖矿代码的运行并弹窗预警，确保用户CPU资源不被消耗占用，保障用户正常的上网体验。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a4b85b787cfe7938.jpg)

360安全卫士推出“挖矿木马防护”功能
<li>
<h3 name="h3-18" id="h3-18">
<a name="_Toc504402203"></a><a name="_Toc503962427"></a> 基于移动端的缓解策略</h3>
</li>
与PC平台相比，移动平台受限于权限限制，并且App应用又通常自己实现内置浏览器功能，所以不能对挖矿木马进行彻底的拦截。

对已有Root权限的手机，可以设置Iptables对挖矿网址进行通信拦截实现防火墙功能。但是，对于普通用户这种方法操作难度高且网址更新存在滞后性；

对没有Root权限的手机，禁用手机浏览器JavaScript特性可以起到一定的防护作用。然而这种方式只能阻止使用浏览器访问网页的挖矿行为，并不能对应用内嵌的浏览器功能进行有效的防护。

[![](https://p4.ssl.qhimg.com/t012215cddff3eeb986.png)](https://p4.ssl.qhimg.com/t012215cddff3eeb986.png)

设置手机浏览器JavaScript

另外，我们建议用户结合上述方法的同时，应当提高个人安全意识，培养良好的使用手机习惯。在选择应用下载途径时，应该尽量选择大型可信站点。不要轻易点击来历不明的链接，当手机使用中异常发热和运行卡顿时，应及时使用安全软件进行扫描检测。


<li>
<h2 name="h2-19" id="h2-19"> 总结</h2>
</li>
<li>
<h3 name="h3-20" id="h3-20">
<a name="_Toc504402205"></a> 发展前景</h3>
</li>
挖矿、勒索成为2017年两大全球性的安全话题，不仅仅由于影响广泛，后果恶劣，更是由于这两者都出现了从PC向移动平台蔓延的趋势。相比PC端，移动终端设备普及率高，携带方便，更替性强，因而安全问题的影响速度更快，传播更广。然而，移动平台在挖矿能力上受限于电池容量和处理器能力，并且在挖矿过程中会导致设备卡顿、发热、电池寿命骤降，甚至出现手机物理损坏问题，就目前来看移动平台还不是一个可持续性生产电子货币的平台。

软件开发者和网站站主一直在寻找能够替代广告、付费、捐赠的新盈利模式。以比特币、门罗币为代表的电子加密货币正在快速增长，现有货币增值并出现新的货币币种，挖矿最终会变得更有利可图。据了解，去年9月份某位网站站主做了一次将广告替换成使用Coinhive挖掘门罗币的尝试，他在60个小时内收益了0.00947门罗币（Monero，代号XMR）按照当时的价格约合$0.89，平均每天0.36 美元，比当时条幅和文本广告的收益要少4~5倍。现在来看门罗币（XMR）价格的一路走高，若以当前价格来计算，在网站相同访问量的情况下挖矿带来的收益是几乎等价于甚至高于广告的收益。

[![](https://p5.ssl.qhimg.com/t0122d2a2a7d6e79f01.png)](https://p5.ssl.qhimg.com/t0122d2a2a7d6e79f01.png)

网站收益统计数据[13]
<li>
<h3 name="h3-21" id="h3-21">
<a name="_Toc504402206"></a> 风险控制</h3>
</li>
尽管当前国外电子货币发展势头较猛，但是不可忽视的是方便灵活的全平台化的挖矿脚本，也让沉寂多年的移动平台挖矿木马注入了新的“活力”。

这种全新的盈利模式，还处在起步阶段，还需要更多的控制和监管。正如最初广告的出现，初衷是为了在不影响体验的情况下，又能达到开发者、网站主和用户的共赢的目的。但是由于管控不严，广告滥用用户的设备资源，出现了大量的恶意广告，不仅严重影响用户体验，还经常伴随着恶意扣费、隐私窃取等恶意行为。挖矿与广告产业的发展会有很多相似之处，虽然能够替代了扰人的广告，但是如果不加以控制，在用户不知情的情况下肆意滥用用户设备进行挖矿，造成用户机器过度损耗。

我们调查中发现，coinhive已经提供了用户告知提示，在启动挖矿程序前会弹出提示框明确告知用户挖矿行为，如果用户取消，则可以终止挖矿，这确实是个好的开始。我们希望更多的矿池提供商，能够进行严格控制，避免被恶意利用。我们将持续关注此类恶意程序的发展。

[![](https://p2.ssl.qhimg.com/t01fae7a0220bcd0941.png)](https://p2.ssl.qhimg.com/t01fae7a0220bcd0941.png)

Coinhive挖矿提示窗



## 附录一：参考资料

[1]比特币价格变化趋势: [https://www.feixiaohao.com/currencies/bitcoin/](https://www.feixiaohao.com/currencies/bitcoin/)

[2] CoinKrypt: How criminals use your phone to mine digital currency:

https://blog.lookout.com/coinkrypt

[3] BadLepricon: Bitcoin gets the mobile malware treatment in Google Play:

[https://blog.lookout.com/badlepricon-bitcoin](https://blog.lookout.com/badlepricon-bitcoin)

[4] Widdit: When mobile mining malware might be legit:

[https://blog.lookout.com/widdit-miner#more-15585](https://blog.lookout.com/widdit-miner#more-15585)

[5] Coin Miner Mobile Malware Returns, Hits Google Play:

http://blog.trendmicro.com/trendlabs-security-intelligence/coin-miner-mobile-malware-returns-hits-google-play/

[6] CPU miner for Litecoin and Bitcoin: https://github.com/pooler/cpuminer

[7] 3 fake Bitcoin wallet apps appear in Google Play Store:

[https://blog.lookout.com/fake-bitcoin-wallet](https://blog.lookout.com/fake-bitcoin-wallet)

[8] Jack of all trades: [https://securelist.com/jack-of-all-trades/83470/](https://securelist.com/jack-of-all-trades/83470/)

[9] 使用Coinhive安卓SDK挖矿的木马: https://twitter.com/fs0c131y/status/949781296187871232

[10] Cryptocurrency mining affects over 500 million people:

[https://blog.adguard.com/en/crypto-mining-fever/](https://blog.adguard.com/en/crypto-mining-fever/)

[11] [Coinhive – Monero JavaScript Mining](https://www.google.com.hk/url?sa=t&amp;rct=j&amp;q=&amp;esrc=s&amp;source=web&amp;cd=1&amp;ved=0ahUKEwi1uoe5o-HYAhUMJpQKHQdCDdsQFggmMAA&amp;url=%68%74%74%70%73%3a%2f%2f%63%6f%69%6e%68%69%76%65%2e%63%6f%6d%2f&amp;usg=AOvVaw1mGp9YsPaKLU2W5zkdwb3D): [https://coinhive.com/](https://coinhive.com/)

[12] 海盗湾植入coinhive挖矿脚本进行挖矿: [https://zh.wikipedia.org/wiki/%E6%B5%B7%E7%9B%9C%E7%81%A3](https://zh.wikipedia.org/wiki/%E6%B5%B7%E7%9B%9C%E7%81%A3)

[13] Coinhive review: Embeddable JavaScript Crypto Miner – 3 days in:

[https://medium.com/@MaxenceCornet/coinhive-review-embeddable-javascript-crypto-miner-806f7024cde8](https://medium.com/@MaxenceCornet/coinhive-review-embeddable-javascript-crypto-miner-806f7024cde8)


