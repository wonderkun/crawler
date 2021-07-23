> 原文链接: https://www.anquanke.com//post/id/216188 


# Defi？Uniswap 项目漏洞教程新骗局


                                阅读量   
                                **115499**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t016553adbc5146eaae.png)](https://p5.ssl.qhimg.com/t016553adbc5146eaae.png)



作者：极光 @ 知道创宇404区块链安全研究团队

## 前言

昨晚突然看到群里的一个消息，`揭秘uniswap-defi项目漏洞-割韭菜新手法`，心想还有这事？

[![](https://p5.ssl.qhimg.com/t01260f2c9e88ba2a1f.jpg)](https://p5.ssl.qhimg.com/t01260f2c9e88ba2a1f.jpg)

而且还是中英文介绍。

[![](https://p2.ssl.qhimg.com/t012367525760675b6e.png)](https://p2.ssl.qhimg.com/t012367525760675b6e.png)

到底什么是`DeFi`？，网络上有很多关于 `DeFi`的定义，目前通用的定义是这样的：`DeFi是自己掌握私钥，以数字货币为主体的金融业务`这个定义包含三个层面的意思：
- 自己掌握私钥
- 以数字货币为主体
- 金融业务
DeFi是Decentralized Finance（去中心化金融）的缩写，也被称做Open Finance。它实际是指用来构建开放式金融系统的去中心化协议，旨在让世界上任何一个人都可以随时随地进行金融活动。

在现有的金融系统中，金融服务主要由中央系统控制和调节，无论是最基本的存取转账、还是贷款或衍生品交易。DeFi则希望通过分布式开源协议建立一套具有透明度、可访问性和包容性的点对点金融系统，将信任风险最小化，让参与者更轻松便捷地获得融资。

几年前区块链行业还没有`DeFi`这个概念，从默默无闻，一跃成为区块链行业的热门话题，`DeFi`只用了短短几年时间。`Uniswap`作为完全部署在以太坊链上的DEX平台，促进ETH和ERC20 代币数字资产之间的自动兑换交易，为`DeFi`发展提供了良好的支持。

作者抓住当下区块链热门话题`DeFi`作为文章主题介绍如何利用<br>`uniswap-defi项目漏洞`割韭菜。很显然经过精心思考。



## 分析

打开教程链接，原文教程提醒

```
Full open source code----only for research and testing, don't cheat using this method
```

[![](https://p0.ssl.qhimg.com/t010113f0f84d78b2a5.png)](https://p0.ssl.qhimg.com/t010113f0f84d78b2a5.png)

作者特别提醒：完全开放源码——仅用于研究和测试，不要使用这种方法作弊。

教程中提到合约代码可以在如下链接下载

```
Click to enter edit mode and copy the code into it 
(download address of the contract code:https://wwr.lanzous.com/i4MJOg6f2rg)
```

[![](https://p2.ssl.qhimg.com/t01ae5ace7d6fed1a39.png)](https://p2.ssl.qhimg.com/t01ae5ace7d6fed1a39.png)

根据教程提供的链接，下载代码查看

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019b109efa75a42492.png)

首先看到`onlyOwner`函数，而且条件判断中的address是硬编码的，这里说一下以太坊中的地址
- 以太坊地址
> 以太坊中的地址的长度为20字节，一字节等于8位，一共160位，所以address其实亦可以用uint160来声明。以太坊钱包地址是以16进制的形式呈现，我们知道一个十六进制的数字占4位，160 ／ 4 = 40，所以钱包地址ca35b7d915458ef540ade6068dfe2f44e8fa733c的长度为40。

很明显，攻击者特意使用uint160来编码地址，起到了障眼法作用。如果不认真看，不会注意到这个address函数转换后的地址。

通过对地址进行转换

[![](https://p3.ssl.qhimg.com/t01d960a4861e45857d.png)](https://p3.ssl.qhimg.com/t01d960a4861e45857d.png)

即：`address(724621317456347144876435459248886471299600550182)` 对应地址：`0x7eed24C6E36AD2c4fef31EC010fc384809050926`，这个地址即位合约实际控制账户地址。

继续往下看原文教程

首先部署合约

[![](https://p4.ssl.qhimg.com/t011f521d3f5115dc7c.png)](https://p4.ssl.qhimg.com/t011f521d3f5115dc7c.png)

然后添加到 `Uniswap v1` 资金池

[![](https://p2.ssl.qhimg.com/t013dd1f63bc3136e25.png)](https://p2.ssl.qhimg.com/t013dd1f63bc3136e25.png)

这里介绍下 `Uniswap`
- Uniswap V1
Uniswap V1基于以太坊区块链为人们提供去中心化的代币兑换服务。Uniswap V1提供了ETH以及ERC20代币兑换的流动性池，它具有当前DeFi项目中最引人注目的去中心化、无须许可、不可停止等特性。

Uniswap V1实现了一种不需要考虑以上特点的去中心化交易所。它不需要用户进行挂单（没有订单），不需要存在需求重叠，可以随买随卖。得益于 ERC20 代币的特性，它也不需要用户将资产存入特定的账户。Uniswap V1模型的优点在于根据公式自动定价，通过供需关系实现自动调价。

Uniswap V1的运行机制的关键在于建立了供给池，这个供给池中存储了 A 和 B 两种货币资产。用户在用 A 兑换 B 的过程中，用户的 A 会发送到供给池，使供给池中的 A 增多，同时，供给池的 B 会发送给用户。这里的关键的问题在于如何给 A 和 B 的兑换提供一个汇率（定价）。<br>
Uniswap V1定价模型非常简洁，它的核心思想是一个简单的公式 x * y = k 。其中 x 和 y 分别代表两种资产的数量，k 是两种资产数量的乘积。

假设乘积 k 是一个固定不变的常量，可以确定当变量 x 的值越大，那么 y 的值就越小；相反 x 的值越小，y 的值就越大。据此可以得出当 x 被增大 p 时，需要将 y 减少 q 才能保持等式的恒定。<br>
为了做一些更实用的工作，将 x 和 y 替换为货币储备金的储备量，这些储备金将被存储在智能合约中。

即用户可以把部署的合约可以添加到`Uniswap V1`中，通过充入资产提供流动性，获得该资金池（交易对）产生的交易手续费分红，过程完全去中心化、无审核上币。

接着

```
You don't have to worry that you will lose money, because other people can only buy and can't sell it  in this contract. When the trading pair is created, you can change for another wallet (the wallet address of the contract can be bought and sold) to buy it, and then test whether it can be sold. Here's the information for selling`

```

[![](https://p3.ssl.qhimg.com/t01de94cc7e9677e9c1.png)](https://p3.ssl.qhimg.com/t01de94cc7e9677e9c1.png)

这是为什么？看看代码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015c3dbfbe69fb4358.png)

合约代币101行，`require(allow[_from] == true)`，即`转账地址from`需要在`allow`这个mapping中为布尔值`true`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013324acd0a94602aa.png)

而修改`allow`在`addAllow`函数中，且需要合约`Owner`权限。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019c0f94b42588237d.png)

通过合约`Ownable`代码第13行可知，`onlyOwner`属性中，只有地址为`724621317456347144876435459248886471299600550182`即前面提到的`0x7eed24C6E36AD2c4fef31EC010fc384809050926`用户可以通过校验，而且是硬编码。这也是原文攻击者为什么使用了以太坊地址的uint160格式来编码地址，而不是直观的十六进制地址。

[![](https://p5.ssl.qhimg.com/t01c9bcc80367192a94.png)](https://p5.ssl.qhimg.com/t01c9bcc80367192a94.png)

最终部署的合约SoloToken直接继承了`Ownable`合约

[![](https://p3.ssl.qhimg.com/t01d6ea929fdecd6fd1.png)](https://p3.ssl.qhimg.com/t01d6ea929fdecd6fd1.png)

即只要用户部署该合约，合约`Owner`权限都在攻击者`0x7eed24C6E36AD2c4fef31EC010fc384809050926`手中。攻击者可以随时转移合约权限。

在教程中攻击者还提到

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a76b81f345d48842.png)

如果你想吸引买家，资金池必须足够大，如果只投入1-2个ETH，其他人将无法购买它，因为基金池太小。即希望部署合约的用户在资金池中添加更多的eth数量。攻击者为什么要单独`Notice`呢？

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01bb204dae222ba865.png)

合约代码第124行，`mint`函数，`Owner`权限用户可以直接增发代币。这是合约最关键部分。即攻击者可以直接在合约中给指定地址增发代币，然后利用增发得来的代币去`Uniswap V1`直接兑换合约部署用户存放在 `Uniswap V1` 资金池中的 `eth` 。这也是为啥教程作者着重提示多添加 `eth` 数量的根本原因。

截止目前，攻击者地址`0x7eed24C6E36AD2c4fef31EC010fc384809050926`中已经获利大约`36eth`。

[![](https://p5.ssl.qhimg.com/t010f8d63ed0eacdc47.png)](https://p5.ssl.qhimg.com/t010f8d63ed0eacdc47.png)



## 总结

`Uniswap` 因无需订单薄即可交易的模型创新引来赞誉，也因投机者和诈骗者的涌入遭到非议，在业内人士看来，`Uniswap` 的自动做市商机制有着特别的价值，作恶的不是`Uniswap`，但恶意与贪婪正在这个去中心化协议中一览无余。

流动性挖矿点燃DeFi烈火，火势烧到去中心化交易所Uniswap。它凭借支持一键兑币、做市可获手续费分红，迅速成为最炙手可热的DeFi应用之一。

财富故事在这里上演，某个新币种可能在一天之内制造出数十倍的涨幅，让参与者加快实现「小目标」；泡沫和罪恶也在此滋生，完全去中心化、无审核上币，让Uniswap成了人人可发币割韭菜的温床。

`DeFi`作为当下区块链热门话题，很容易吸引人们的注意。攻击者利用人们贪图便宜的好奇心理。使用所谓的 `uniswap-defi项目漏洞` 教程一步一步带用户入坑。以当下区块链中最火的`DeFi`类为主题，分享了 `揭秘uniswap-defi项目漏洞-割韭菜新手法` 教程。如果用户不注意看合约代码，很容易掉入攻击者精心构造的陷阱中去。成为真正的`韭菜`。



## REF

[1] UNISWAP issuing tokens-enhancing tokens (consumers can only buy but can not sell)

[https://note.youdao.com/ynoteshare1/index.html?id=a41d926f5bcbe3f69ddef765ced5e27b&amp;type=note?auto](https://note.youdao.com/ynoteshare1/index.html?id=a41d926f5bcbe3f69ddef765ced5e27b&amp;type=note?auto)

[2] 代币合约

[https://wwr.lanzous.com/i4MJOg6f2rg](https://wwr.lanzous.com/i4MJOg6f2rg)
