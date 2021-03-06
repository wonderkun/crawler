> 原文链接: https://www.anquanke.com//post/id/95873 


# 360CERT——区块链技术安全讨论


                                阅读量   
                                **172369**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



![](https://p4.ssl.qhimg.com/t0124f230d800c2e3da.png)
<td width="548">安全报告：区块链技术安全讨论</td>
<td width="548">报告编号：B6-2018-012301</td>
<td width="548">报告来源：360网络安全响应中心</td>
<td width="548">报告作者：360CERT</td>
<td width="548">更新日期：2018年1月23日</td>

## 0x00 背景介绍

区块链技术是金融科技（Fintech）领域的一项重要技术创新。

作为分布式记账（Distributed Ledger Technology，DLT）平台的核心技术，区块链被认为在金融、征信、物联网、经济贸易结算、资产管理等众多领域都拥有广泛的应用前景。区块链技术自身尚处于快速发展的初级阶段，现有区块链系统在设计和实现中利用了分布式系统、密码学、博弈论、网络协议等诸多学科的知识，为学习原理和实践应用都带来了不小的挑战。

区块链属于一种去中心化的记录技术。参与到系统上的节点，可能不属于同一组织、彼此无需信任；区块链数据由所有节点共同维护，每个参与维护节点都能复制获得一份完整记录的拷贝，由此可以看出区块链技术的特点：
- 维护一条不断增长的链，只可能添加记录，而发生过的记录都不可篡改；
- 去中心化，或者说多中心化，无需集中的控制而能达成共识，实现上尽量分布式；
- 通过密码学的机制来确保交易无法抵赖和破坏，并尽量保护用户信息和记录的隐私性。
虽然单纯从区块链理解，仅仅是一种数据记录技术，或者是一种去中心化的分布式数据库存储技术，但如果和智能合约结合扩展，就能让其提供更多复杂的操作，现在活跃的各个数字货币就是其中一种表现形式。



## 0x01 区块链安全性思考

由于区块链技术的特性，在设计之处就想要从不同维度解决一部分安全问题：

### 01 Hash唯一性

在blockchain中，每一个区块和Hash都是以一一对应的，每个Hash都是由区块头通过sha256计算得到的。因为区块头中包含了当前区块体的Hash和上一个区块的Hash，所以如果当前区块内容改变或者上一个区块Hash改变，就一定会引起当前区块Hash改变。如果有人修改了一个区块，该区块的 Hash 就变了。为了让后面的区块还能连到它，该人必须同时修改后面所有的区块，否则被改掉的区块就脱离区块链了。由于区块计算的算力需求强度很大，同时修改多个区块几乎是不可能的。

由于这样的联动机制，块链保证了自身的可靠性，数据一旦写入，就无法被篡改。这就像历史一样，发生了就是发生了，从此再无法改变，确保了数据的唯一性。

### 02 密码学安全性

以比特币为例，数字货币采用了非对称加密，所有的数据存储和记录都有数字签名作为凭据，非对称加密保证了支付的可靠性。

### 03 身份验证

在数字货币交易过程中，由一个地址到另一个地址的数据转移都会对其进行验证：

– 上一笔交易的Hash(验证货币的由来)

– 本次交易的双方地址

– 支付方的公钥

– 支付方式的私钥生成的数字签名

验证交易是否成功属实会经过如下几步：

– 找到上一笔交易确认货币来源

– 计算对方公钥指纹并与其地址比对，保证公钥的真实性

– 使用公钥解开数字签名，保证私钥真实性

### 04 去中心化的分布式设计

针对区块链来说，账本数据全部公开或者部分公开，强调的是账本数据多副本存在，不能存在数据丢失的风险，区块链当前采用的解决方案就是全分布式存储，网络中有许多个全节点，同步所有账本数据（有些同步部分，当然每个数据存储的副本足够多），这样网络中的副本足够多，就可以满足高可用的要求，丢失数据的风险就会低很多。所以建议部署区块链网络时，全节点尽量分散，分散在不同地理位置、不同的基础服务提供商、不同的利益体等。

### 05 传输安全性

在传输过程中，数据还未持久化，这部分空中数据会采用HTTP+SSL(也有采用websocket+websocketS)进行处理，从而保证数据在网络传输中防篡改且加密处理。



## 0x02 数字货币安全性思考

### <a name="_Toc504419707"></a>01 BTC

比特币（Bitcoin，代号BTC）是一种用去中心化、全球通用、不需第三方机构或个人，基于区块链作为支付技术的电子加密货币。比特币由中本聪于2009年1月3日，基于无国界的对等网络，用共识主动性开源软件发明创立。比特币也是目前知名度与市场总值最高的加密货币。

#### 比特币区块结构

![](https://p0.ssl.qhimg.com/t01ca57704c777e31e3.png)

#### 钱包和交易

比特币钱包的地址就是公钥通过 Base58 算法编码后的一段字符串，使用该算法可以将公钥中的一些不可见字符编码成平时常见的字符。Base58 相对于 Base64 来说消除了非字母或数字的字符，如：“+”和“/”，同时还消除了那些容易产生混淆的字符，如数字 0 和大写字母 O，大写字母 I 和小写字母 l。这一段用作比特币钱包地址的字符串就相当于一个比特币账户。

交易属于比特币中的核心部分，区块链应用到数字货币上也是为提供更安全可靠的交易。交易之前会先确认每一笔笔交易的真实性，如果是真实的，交易记录便会写入到新的区块中去，而一旦加入到区块链中了也就意味着再也不能被撤回和修改。

#### 交易验证流程大概为：

1. 验证交易双方的钱包地址，也就是双方的公钥。

2. 支付方的上一笔的交易输出，前面也说到了钱包里面是没有存放你的比特币数量的，而你每一笔交易都会产生交易输出记录到区块链中。通过交易输出可以确认支付方是否能够支付一定数量的比特币。

3. 支付方的私钥生成的数字签名。如果使用支付方的公钥能解开这个数字签名便可以确认支付方的身份是真实的，而不是有人恶意的使用当前的支付方的钱包地址在做交易。

一旦这些信息都能得到确认便可以将交易信息写入到新的区块中去，完成交易。受比特币区块大小的限制（目前的为 1MB，一笔交易信息大概需要 500 多字节），一个区块最多只能包含 2000 多笔的交易。因为区块链中记录了所有的交易信息，所以每个比特币钱包的交易记录和币的数量都是可以被查到的，但是只要没有对外公开承认钱包地址是属于你的，也不会有人知道一个钱包地址的真实拥有者。

还有一种交易叫做 coinbase 交易，当矿工挖到一个新的区块时，他会获得挖矿奖励。挖矿奖励就是通过 coinbase 交易拿到手的，也一样是需要把交易信息添加到新的区块中去，但是 coinbase 交易不需要引用之前的交易输出。

#### 安全问题

比特币基于区块链，具有去中心化结构，用户通过一个公开的地址和密钥来宣示所有权。某种程度上，谁掌握了这个密钥，谁就实质性地拥有了对应地址中的比特币资产。而区块链的防篡改特征，是指比特币的交易记录不可篡改，而非密钥不会丢失。同时，也正因为区块链不可篡改，密钥一旦丢失，也意味着不可能通过修改区块链记录来拿回比特币。

因此针对比特币的盗币事件屡有发生，主要是通过下面三个手段：

1. 交易平台监守自盗

2. 交易所遭受黑客攻击

3. 用户交易账户被盗

交易平台监守自盗可以向平台索回，但是黑客攻击导致的盗币，很难被追回。因为黑客一旦盗取比特币，接下来便会通过混币等手段进行洗白，除非有国家力量强力介入，否则追回的可能性仅仅停留在理论层面。

### 02 ETH

以太币（Ether，代号ETH）为以太坊区块链上的代币，可在许多加密货币的外汇市场上交易，它也是以太坊上用来支付交易手续费和运算服务的媒介。以太坊（Ethereum）是一个开源的有智能合约功能的公共区块链平台。通过其专用加密货币以太币提供去中心化的虚拟机（称为“以太虚拟机”Ethereum Virtual Machine）来处理点对点合约。

#### 智能合约

以太坊与比特币最大的一个区别——提供了一个功能更强大的合约编程环境。如果说比特币的功能只是数字货币本身，那么在以太坊上，用户还可以编写智能合约应用程序，直接将区块链技术的发展带入到 2.0 时代。

![](https://p4.ssl.qhimg.com/t011a3e0717ccadb17a.jpg)

以太坊中的智能合约是运行在虚拟机上的，也就是通常说的 EVM（Ethereum Virtual Machine，以太坊虚拟机）。这是一个智能合约的沙盒，合约存储在以太坊的区块链上，并被编译为以太坊虚拟机字节码，通过虚拟机来运行智能合约。由于这个中间层的存在，以太坊也实现了多种语言的合约代码编译，网络中的每个以太坊节点运行 EVM 实现并执行相同的指令。如果说比特币是二维世界的话，那么以太坊就是三维世界，可以实现无数个不同的二维世界。

#### 安全问题

ETH最大的特点就是智能合约，而智能合约漏洞也就导致了ETH的安全问题。

2016年黑客通过The Dao，利用智能合约中的漏洞，成功盗取360万以太币。THE DAO持有近15%的以太币总数，因此这次事件对以太坊网络及其加密币都产生了负面影响。

The DAO事件发生后，以太坊创始人Vitalik Buterin提议修改以太坊代码，对以太坊区块链实施硬分叉，将黑客盗取资金的交易记录回滚，得到了社区大部分矿工的支持，但也遭到了少数人的强烈反对。最终坚持不同意回滚的少数矿工们将他们挖出的区块链命名为Ethereum Classic（以太坊经典，简称ETC），导致了以太坊社区的分裂。在虚拟货币历史上，这是第一次，也可能唯一一次由于安全问题导致的区块链分叉事件。

无独有偶2017年7月19日, 多重签名钱包Parity1.5及以上版本出现安全漏洞,15万个ETH被盗,共价值3000万美元。

两次被盗事件都是因为智能合约中的漏洞。让我们看到，虚拟货币的安全不仅仅是平台和个人，区块链上的应用，也是我们应该关注的内容。

### 03 XMR

门罗币（Monero，代号XMR）是一个创建于2014年4月开源加密货币，它着重于隐私、分权和可扩展性。与自比特币衍生的许多加密货币不同，Monero基于CryptoNote协议，并在区块链模糊化方面有显著的算法差异。

#### 隐蔽地址

隐蔽地址是为了解决输入输出地址关联性的问题。每当发送者要给接收者发送一笔金额的时候，他会首先通过接收者的地址（每次都重新生成），利用椭圆曲线加密算出一个一次性的公钥。然后发送者将这个公钥连同一个附加信息发送到区块链上，接收方可以根据自己的私钥来检测每个交易块，从而确定发送方是否已经发送了这笔金额。当接收方要使用这笔金额时，可以根据自己的私钥以及交易信息计算出来一个签名私钥，用这个私钥对交易进行签名即可。

#### 环签名

隐蔽地址虽然能保证接收者地址每次都变化，从而让外部攻击者看不出地址关联性，但并不能保证发送者与接收者之间的匿名性。因此门罗币提出了一个环签名的方案——事实上，在古代就已经有类似的思想了：如图5所示，联名上书的时候，上书人的名字可以写成一个环形，由于环中各个名字的地位看上去彼此相等，因此外界很难猜测发起人是谁。这就是环签名。

![](https://p5.ssl.qhimg.com/t01416b9e638c293583.jpg)

除了交易地址，交易金额也会暴露部分隐私。门罗币还提供了一种叫做环状保密交易（RingCT）的技术来同时隐藏交易地址以及交易金额。这项技术正在逐步部署来达到真正的匿名。这项技术采用了多层连接自发匿名组签名（Multi-layered Linkable Spontaneous Anonymous Group signature）的协议。

#### 安全问题

比特币交易私密性方面做的不太好，关于货币隐私的两个基本属性：

1. 不可链接性（Unlinkability）：无法证明两个交易是发送给同一个人的，也就是无法知道交易的接收者是谁。

2. 不可追踪性（Untraceability）：无法知道交易的发送者是谁。

比特币交易要发送地址信息，很明显不符合之上的要求。门罗币通过隐蔽地址来保证不可链接性，通过环签名来保证不可追踪性，从而给用户的交易信息提供了很好的隐私性。另一方面，比特币挖矿主要依赖于大量专业化的专用集成电路（ASIC）。它的算法在ASIC上的运行速度远超于在标准家庭电脑或者笔记本电脑上运行。相比之下，门罗币的挖矿算法要精良得多。它并不依赖于ASIC，使用任何CPU或GPU都可以完成，这就意味着门罗币具有更低的挖掘门槛。

门罗币的这些特性，使其成为黑产挖矿的不二之选。过去的一段时间，出现了许多以门罗币挖矿为目的的网络攻击事件。

### 04 小结

在以太坊这种平台区块链上，如果运行智能合约，应用程序出现漏洞，同样也会威胁其上的数字资产。

以太坊解决了比特币的单应用的局限，使得区块链像一个操作系统，开发者可以在其上搭建自己的“应用”。门罗币降低了挖矿的门槛，同时又满足了交易私密性需求。这些特性都符合黑产的需要，过去的一段时间，以门罗币挖矿为目的的网络攻击事件时有发生。



## 0x03 交易平台安全性思考

随着区块链技术的迅速发展,使得虚拟货币渐渐走入的大众的视线。随之而来的就是大量的虚拟币交易平台。虚拟货币交易平台就是为用户提供虚拟货币与虚拟货币之间兑换的平台，部分平台还提供人民币与虚拟货币的p2p兑换服务。现在交易平台平均每天的交易额都是数以亿计，然而交易平台背后的经营者能力与平台的自身的安全性并没有很好的保障。从14年至今据不完全统计，单纯由于交易所安全性导致的直接损失就达到了1.8亿美元之多。

![](https://p1.ssl.qhimg.com/t015b2e30ea44d4de5e.jpg)

![](https://p3.ssl.qhimg.com/t01fc2c6a99ca48c734.jpg)

随着虚拟币的水涨船高，交易所就成了黑客们的首要目标，据统计入侵一家交易所给黑客带来的直接利益大约1000万美元左右，然而交易所的安全性参差不齐和各个国家对这类平台基本都暂时没有好的管控策略，这给黑客带来了很大的便利，同时也直接威胁着用户的资金安全。

### <a name="_Toc504419712"></a>01平台被黑事件回顾
- **比特儿(Bter.com) 比特币交易平台被盗事件**
2014-08-15

事件简介：

比特儿是一家中国的山寨币交易所。NXT等山寨币都在上面交易。

由于POS币的钱包必须上线运行才能获取利息。因此NXT钱包必须在线运行，给了入侵的机会。POS币不能冷钱包保存，暴露出POS的重大安全隐患。黑客盗走NXT后与平台方通过交易留言进行了谈判：

![](https://p3.ssl.qhimg.com/t016d3b2bba8ada2f0e.png)

并要求平台方支付BTC作为赎金换回NXT

![](https://p5.ssl.qhimg.com/t0161773ea8f82259e9.png)

最终平台支付了110个BTC，却未能完全赎回NXT，只能要求社区回滚NXT的交易区块。

本次比特儿被黑是历史上第一次完全公开展现的网络犯罪，暴露出交易平台和数字货币在当时没有监管野蛮生长的严肃问题。
- **以太币组织The DAO被黑事件**
2016-06

事件简介：

以太币的去中心化组织The Dao被黑，价值逾5000万美元的以太币外溢出DAO的钱包。以太币（ETH）市场价格瞬间缩水，从记录高位21.50美元跌至15.28美元，跌幅逾23%。

在此前的智能合约写法中，有三个严重漏洞，黑客也正是利用这几个漏洞攻击The DAO窃取以太币。
<li>
**fallback****函数调用**
</li>
向合约地址发送币有两种写法：

```
address addr = 地址;

if (!addr.call.value(20 ether)()) `{`

throw;

`}`
```

```
address addr = 地址;

if (!addr.send(20 ether)) `{`   

throw;

`}`
```

二者都是发送20个ether，都是一个新的message call，不同的是这两个调用的gasli   mit不一样。send()给予0的gas（相当于**call.gas(0).value()()**)，而**call.value()()**给予全部（当前剩余）的gas。当我们调用某个智能合约时，如果指定的函数找不到，或者根本就没指定调用哪个函数（如发送ether）时，fallback函数就会被调用。

当通过**addr.call.value()()**的方式发送ether，和send()一样，fallback函数会被调用，但是传递给fallback函数可用的气是当前剩余的所有gas，如果精心设计一个fallback就能影响到系统，如写storage，重新调用新的智能合约等等。
- **递归调用 **
一段用户从智能合约中取款的代码如下：

```
function withdrawBalance() `{`   

amountToWithdraw = userBalances[msg.sender];   

if（ amountToWithdraw &gt; 0) `{`   

if (!(msg.sender.call.value(amountToWithdraw)())) `{`       

        throw;   

    `}`   

    userBalances[msg.sender] = 0;

`}`

`}`
```

如果付款方的合约账户中有1000个ether，而取款方有10个ether，此处就有严重的递归调用问题，取款方可以将1000个ether全部取走。
- **调用深度限制 **
合约可以通过message call调用其他智能合约， 被调用的合约继续通过message call在调用其他合约，这样的嵌套调用深度限制为1024。

```
function sendether() `{`   

address addr = 地址;   

addr.send(20 ether);   

var thesendok = true;

`}`
```

如果攻击者制造以上的1023个嵌套调用，之后再调用**sendether()**，就可以让**add.send(20 ether)**失效，而其他执行成功：

```
function hack() `{`   

    var count = 0;   

    while (count &lt; 1023) `{`       

        this.hack();       

        count++;   

        `}`   

       if (count == 1023) `{`       

       thecallingaddr.call("sendether");   

       `}`

`}`
```

在DAO的代码中：

```
function splitDAO(uint _proposalID, address _newCurator) noEther onlyTokenholders returns(bool _success) `{`   

    ...   

    uint fundsToBeMoved = (balances[msg.sender] * p.splitData[0].splitBalance) / p.splitData[0].totalSupply;   

    if (p.splitData[0].newDAO.createTokenProxy.value(fundsToBeMoved)(msg.sender) == false) throw;   

    ...   

    withdrawRewardFor(msg.sender);   

    totalSupply -= balances[msg.sender];   

    balances[msg.sender] = 0;   

    paidOut[msg.sender] = 0;   

    return true;

`}`
```

当合约执行到**withdrawRewardFor(msg.sender);**进入到函数**withdrawRewardFor**判断

```
function withdrawRewardFor(address _account) noEther internal returns(bool _success) `{`   

    ...   

    if(!rewardAccount.payOut(_account, reward)) //漏洞代码   

        throw;   

        ...

`}`
```

payOut定义如下:

```
function payOut(address _recipient, uint _amount) returns(bool) `{`   

    ...   

    if(_recipient.call.value(_amount)) //漏洞代码     

    PayOut(_recipient, _amount);   

    return true;

`}` else `{`   

    return false;

`}`

`}`
```

和此前的举例类似，DAO通过**addr.call.value()()**发送以太币而没有选择**send()**从而黑客只需要创建fallback再次调用**splitDAO()**即可转移多份以太币，PoC如下:

```
p.splitData[0].newDAO.createTokenProxy.value(fundsToBeMoved)(msg.sender)
```

The DAO事件给整个以太坊社区带来了重大影响，也导致了之后的硬分叉和ETC(以太经典)的剥离。
<li>
**Bitfinex****遭黑客攻击事件**
</li>
2016-08

**事件简介： **

Bitfinex是交易比特币、ether和莱特币等数字货币的最大交易所之一。

根据Bitfinex在8月2日凌晨发布的公告，该交易所在发现了一个安全漏洞后便停止了交易。发布在官网上的声明表示：

![](https://p3.ssl.qhimg.com/t0140c2c112962791df.jpg)

Bitfinex负责社区和产品开发的主管塔克特(Zane Tackett)证实，119,756个比特币遭窃，该公司已经知道相关系统是如何被入侵的。以周二的价格计算，失窃比特币价值约6,500万美元，受此消息影响，全球比特币价格应声下跌25%。

![](https://p4.ssl.qhimg.com/t013ce9a39aa64fd49a.png)

随后Bitfinex官网发布公告称这次损失将由平台上所有用户共同承担，这将导致每位用户的账户平均损失36%

对于类似比特币这样的数字货币，由于是通过数学算法挖矿形成，与实体质地的纸币不同，这些数字货币交易的安全性就完全体现在交易所的风险控制能力以及防黑客能力上。
<li>
**Parity****多重签名钱包被盗事件**
</li>
2017-07

**事件简介：   **

Parity是一款多重签名钱包，是目前使用最广泛的以太坊钱包之一，创始人兼CTO 是以太坊前CTO黄皮书作者Gavin Woods。

7 月 19 日，Parity发布安全警报，警告其钱包软件1. 5 版本及之后的版本存在一个漏洞。据该公司的报告，确认有150，000ETH(大约价值 3000 万美元)被盗。据Parity所说，漏洞是由一种叫做wallet.sol的多重签名合约出现bug导致。后来，白帽黑客找回了大约377,000 受影响的ETH。

![](https://p4.ssl.qhimg.com/t019d9dc350a68ec06e.png)

本次攻击造成了以太币价格的震荡，Coindesk的数据显示，事件曝光后以太币价格一度从235美元下跌至196美元左右。此次事件主要是由于合约代码不严谨导致的。我们可以从区块浏览器看到黑客的资金地址:

![](https://p1.ssl.qhimg.com/t016df44cb32d6ecc58.png)

可以看到，一共盗取了153,037 个ETH，受到影响的合约代码均为Parity的创始人Gavin Wood写的Multi-Sig库代码。通过分析代码可以确定核心问题在于越权的函数调用，合约接口必须精心设计和明确定义访问权限，或者更进一步说，合约的设计必须符合某种成熟的模式，或者标准，合约代码部署前最好交由专业的机构进行评审。否则，一个不起眼的代码就会让你丢掉所有的钱。
<li>
**USDT****发行方Tether遭受黑客攻击事件**
</li>
2017-12

**事件简介：**

Tether公司是USDT代币的发行公司——USDT是一种与美元挂钩的加密货币，如今正在被交易所广泛用于进行交易。该公司在公告中声称其系统遭受攻击，已经导致价值3000万美元的USDT代币被盗。

![](https://p1.ssl.qhimg.com/t016dd75ef5fd3dcb04.png)

被盗的代币不会再赎回，但Tether公司表示他们正在试图恢复令牌，以确保这些交易所不再交易或引入这些被盗的资金，不让这些资金回到加密货币经济。此次被黑事件后，比特币的价格下降了5.4%，是11月13日以来的最高纪录。然而，Tether被盗声明一出，国外社区有用户认为，该地址中被盗的3000万美元只是Tether掩耳盗铃的第一步。实际面临的兑付危机远远不止3000万美元。此次事件不仅单纯的一次虚拟币被盗事件同时导致了Tether的信任危机。
<li>
**Youbite****交易所被入侵事件**
</li>
2017-12-19

**事件简介：**

12月19日，韩国数字货币交易所Youbite宣布在当天下午4时（北京时间3时）左右，交易平台受到黑客入侵，造成的损失相当于平台内总资产的17%。 这家平台是韩国一家市场份额较小的数字货币交易平台，在今年4月，这家平台也曾经遭受过黑客攻击，损失了近4000个比特币。

![](https://p0.ssl.qhimg.com/t018060c7d1bfe47442.png)

Youbit表示，在4月份遭遇黑客攻击之后，其加强了安全策略，将其余83％的交易所资金都安全地存放在冷钱包里。尽管如此，运营该交易所的公司Yaipan还是于本周二申请了破产，并停止了平台交易。公告显示，该交易所将所有客户的资产价值减记至市场价值的75%，客户可立即提取这部分资产。该公司表示，将在破产程序结束时偿还剩余的资金，届时将提出保险索赔并出售公司的经营权。

### <a name="_Toc504419713"></a>02小结

虚拟币的火热，直接搅动着金融市场与科技市场，也面临着各种安全问题。现在各个国家也开始对区块链市场与虚拟币市场相继出台政策与治理方案，对交易所也开始纳入管控范围，韩国前段时间对其国家7家大型交易所进行了安全测试均被成功入侵，但每个交易所每天交易量是数以亿计的。可见这类安全问题不是个例，作为虚拟币交易平台，是否有资质有能力保护在线虚拟货币的安全性成为一个值得考究的问题，虚拟币已经渐渐的从网络进入到现实世界中，然而这个过程的进步同样带来了很大的隐患，这也促使着政府企业以及个人对交易平台以及虚拟币本身更加的慎重选择与投入。



## 0x04 区块链在安全行业的应用

区块链社区非常活跃，人们经常认为，这项技术不仅有效地推动了虚拟货币的发展，而且还加强了现有的安全解决方案，从区块链角度解决了一些安全问题。

列举几个区块链技术的安全用途：

### 01 更安全的认证机制

根据区块链技术的特性，设备可以以对等的方式识别和交互，而不需要第三方权威。伴随着双重身份验证，伪造数字安全证书成为不可能，使得网络结构具有更好的安全性。比如应用到密码验证服务，物联网设备认证。

### 02 更安全的数据保护

在基于区块链的系统中，存储的元数据分散在分布式账本中，不能在一个集中点收集，篡改或者删除。其中的数据，具有更好的完整性，可靠性以及不可抵赖性。可以应用到公共数据存储场景，比如产权记录，金融记录。

### 03 更安全的基础设施

利用区块链分布式特性，可以提供一种分散式平台，通过这种系统，可以访问和利用共享的带宽，这种方式远优于带宽有限的单服务器集中模型。去中心化的平台可以降低DDoS成功的风险，更好的保护基础设施。比如网站，DNS解析服务等。
