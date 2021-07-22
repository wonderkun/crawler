> 原文链接: https://www.anquanke.com//post/id/242446 


# PancakeBunny攻击事件复盘分析


                                阅读量   
                                **139109**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01a3bf216410b079f3.png)](https://p2.ssl.qhimg.com/t01a3bf216410b079f3.png)



## 事件背景

PancakeBunny致力于通过为用户提供一种简便的方法，通过Binance Smart Chain自动组合其收益，来支持底层的DeFi生态系统。

零时科技区块链安全情报平台监控到消息，北京时间2021年5月20日，PancakeBunny官方发推文称PancakeBunny遭到闪电贷攻击，导致Bunny价格暴跌，零时科技安全团队及时对该安全事件进行复盘分析。

[![](https://p3.ssl.qhimg.com/t01091bc3288f83debe.png)](https://p3.ssl.qhimg.com/t01091bc3288f83debe.png)



## 事件分析

**攻击信息**

通过零时科技安全团队初步追踪分析，此次攻击信息如下：

攻击者钱包地址：

[https://bscscan.com/address/0xa0acc61547f6bd066f7c9663c17a312b6ad7e187](https://bscscan.com/address/0xa0acc61547f6bd066f7c9663c17a312b6ad7e187)

攻击者合约地址：

[https://bscscan.com/address/0xcc598232a75fb1b361510bce4ca39d7bc39cf498](https://bscscan.com/address/0xcc598232a75fb1b361510bce4ca39d7bc39cf498)

攻击者交易一：

[https://bscscan.com/tx/0x88fcffc3256faac76cde4bbd0df6ea3603b1438a5a0409b2e2b91e7c2ba3371a](https://bscscan.com/tx/0x88fcffc3256faac76cde4bbd0df6ea3603b1438a5a0409b2e2b91e7c2ba3371a)

攻击者交易二：

[https://bscscan.com/tx/0x897c2de73dd55d7701e1b69ffb3a17b0f4801ced88b0c75fe1551c5fcce6a979](https://bscscan.com/tx/0x897c2de73dd55d7701e1b69ffb3a17b0f4801ced88b0c75fe1551c5fcce6a979)

VaultFlipToFlip合约地址：

[https://bscscan.com/address/0xd415e6caa8af7cc17b7abd872a42d5f2c90838ea#code](https://bscscan.com/address/0xd415e6caa8af7cc17b7abd872a42d5f2c90838ea#code)

BunnyMinterV2合约地址：

[https://bscscan.com/address/0x819eea71d3f93bb604816f1797d4828c90219b5d#code](https://bscscan.com/address/0x819eea71d3f93bb604816f1797d4828c90219b5d#code)



## 攻击过程

以下将拆解攻击者的两笔交易，方便读者更清晰的了解攻击过程。

**攻击者第一笔交易**

[![](https://p3.ssl.qhimg.com/t019062d72add03fbb6.png)](https://p3.ssl.qhimg.com/t019062d72add03fbb6.png)

该笔交易中，攻击者使用1枚BNB，并在提供流动性时对半分为0.5枚BNB和189枚USDT，提供流动性后得到USDT-BNB LP，之后将该LP存入Bunny池子。

**攻击者第二笔交易**

第二笔交易中操作较多，也是此次攻击的主要部分，这里将该交易分解为11个步，并进行逐条说明：

[![](https://p2.ssl.qhimg.com/t014062035a619e166b.png)](https://p2.ssl.qhimg.com/t014062035a619e166b.png)

第一步：攻击者首先从PancakeSwap中利用闪电贷借出约232万枚BNB，再从ForTube中利用闪电贷借出296万USDT，之后将7744枚BNB和296万枚USDT转到BNB-USDT池子中添加流动性，获得对应的14万枚BNB-USDT LP。

第二步：将第一步中借到的232万枚BNB在PancakeSwap池中兑换为382万枚USDT（这里已经可以控制价格，大量BNB代币进入池子，BNB价格变的极低）

第三步：调用VaultFlipToFlip合约getReward方法进行取币。（第三步至第九步均为getReward方法调用相关参数进行的代币计算）

第四步：从BNB-USDT池子中取出之前第一步中加入的流动性资金296万枚USDT和7744枚BNB。

第五步：将296万枚USDT换成231万枚BNB。（第二步中已经将BNB价格控制的很低，所以这里可以兑换大量BNB）

[![](https://p0.ssl.qhimg.com/t01cc3e605615c2bc6b.png)](https://p0.ssl.qhimg.com/t01cc3e605615c2bc6b.png)

第六步：将第五步中获取一半BNB，也就是115万枚BNB换成17万枚Bunny。

第七步：将剩余115万枚BNB转入BNB-Bunny池中添加流动性，获得对应LP Token。

第八步：将第四步中取出的流动性资金7744枚BNB，以1：1的比例转入BNB-Bunny池中增加流动性。

第九步：将之前获得的所有LP token添加到PancakeSwap，最终获得697万枚Bunny。

[![](https://p4.ssl.qhimg.com/t01294b52890c777ecc.png)](https://p4.ssl.qhimg.com/t01294b52890c777ecc.png)

第十步：将获取的697万枚Bunny资金转换为BNB和USDT，并给攻击者钱包地址转入69万枚Bunny。

第十一步：归还闪电贷借出的资金，并给攻击者钱包地址转入11万枚BNB转入。

**至此**

攻击者通过此次闪电贷攻击共获取11万枚BNB和69万枚Bunny，但本次攻击者成功的原因不仅仅只利用了闪电贷，除了闪电贷之外，Bunny的合约代码也存在安全风险，在第二笔交易的第三步至第九步获取到巨额Bunny代币均为getReward方法调用所产生的逻辑，这里我们继续来看整个攻击流程涉及的代码问题。



## 攻击成功的原因

通过前面的分析，攻击者已将大量资金注入池子，并通过VaultFlipToFlip合约中getReward方法来获取奖励，如下图所示：<br>[![](https://p1.ssl.qhimg.com/t012cf92f12787faff0.png)](https://p1.ssl.qhimg.com/t012cf92f12787faff0.png)

getReward方法中，会进一步调用 BunnyMinterV2合约中mintForV2方法来为调用者铸造Bunny代币奖励，继续跟进mintForV2方法，如下图：

[![](https://p4.ssl.qhimg.com/t01c7312b6a6c69bf7f.png)](https://p4.ssl.qhimg.com/t01c7312b6a6c69bf7f.png)

mintForV2方法中，最终铸币的数量mintBunny变量是由valueInBNB变量通过简单计算得到，而valueInBNB变量是通过PriceCalculator合约中valueOfAsset方法得到，继续跟进，如下图：

[![](https://p5.ssl.qhimg.com/t01063ab83f28175764.png)](https://p5.ssl.qhimg.com/t01063ab83f28175764.png)

valueOfAsset方法中，valueInBNB变量是通过amount和reserve0以及其他变量计算得出，amount值是mintForV2方法中传入的bunnyBNBAmount变量，该值本身也是一个非常大的值，由于目前的池子中存在大量BNB（攻击过程中六，七，八步存入的大量资金），导致reserve0是一个非常大的数值，计算后valueInBNB变量值变大，最终mintBunny变大铸造了大量Bunny代币。

目前，PancakeBunny官方已对本次攻击涉及的LP代币价格问题和代码中的计算问题进行了修改，并提供了补偿方案。



## 总结

通过此次攻击事件来看，攻击者主要利用闪电贷操纵价格，并通过代码中铸币数量的计算缺陷，最终获得了大量铸币，从中获利。DeFi项目中类似的闪电贷攻击事件居多，为何还会频频发生，对于DeFi项目而言，合约代码的安全，代币价格的相对稳定，旧版本的及时更新都是保证项目安全极其重要的部分，任何细节的马虎都可能导致项目及用户资金受到损失。对于此类闪电贷攻击事件，零时科技安全团队给出以下建议：

### <a class="reference-link" name="%E5%AE%89%E5%85%A8%E5%BB%BA%E8%AE%AE"></a>安全建议

对于合约代码安全，可找多家安全审计公司进行审计。

对LP价格及获取奖励的铸币代码块，应根据业务逻辑进行严格审核演算，避免出现参数可控制导致大量铸币问题。

使用可信的并且安全可靠的预言机，如Chainlink去中心化预言机或者Alpha团队的LP价格计算方式。

对敏感性较强的代码，要做到及时更新完善。
