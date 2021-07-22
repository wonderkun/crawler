> 原文链接: https://www.anquanke.com//post/id/234657 


# DODO攻击事件分析


                                阅读量   
                                **205800**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t015ec33a2265e61e87.png)](https://p1.ssl.qhimg.com/t015ec33a2265e61e87.png)



## 事件背景

DODO是基于主动做市商算法的下一代链上流动性基础设施。DODO作为一个去中心化交易平台，采用资金池模式，纯链上交易。支持新资产的无成本发行。

零时科技区块链安全情报平台监控到消息，北京时间2021年3月9日，DODO官方发推称DODO V2资金池wCRES/USDT遭到黑客攻击，已暂时禁用DODO上的资金池创建，并表示其他资金池都是安全的。

[![](https://p4.ssl.qhimg.com/t01b7e04eeb2c9e00c0.png)](https://p4.ssl.qhimg.com/t01b7e04eeb2c9e00c0.png)

零时科技安全团队对该安全事件进行复盘分析。



## 事件分析

通过初步分析，DODO V2资金池遭攻击事件中涉及的地址如下：

被攻击的DLP合约地址：**https://cn.etherscan.com/address/0x051ebd717311350f1684f89335bed4abd083a2b6#code**

攻击交易：**https://cn.etherscan.com/tx/0x395675b56370a9f5fe8b32badfa80043f5291443bd6c8273900476880fb5221e**

攻击者地址：**https://cn.etherscan.com/address/0x368a6558255bccac517da5106647d8182c571b23**

攻击者合约：**https://cn.etherscan.com/address/0x910fd17b9bfc42a6eea822912f036ef5a080be8a#code**

空气币FUSDT：**https://cn.etherscan.com/token/0xf2df8794f8f99f1ba4d8adc468ebff2e47cd7010**

空气币 FDO：**https://cn.etherscan.com/token/0x7f4e7fb900e0ec043718d05caee549805cab22c8**

初步了解后，继续通过bloxy.info分析交易详情，如下图：

[![](https://p0.ssl.qhimg.com/t014d71d26df2ee54f3.png)](https://p0.ssl.qhimg.com/t014d71d26df2ee54f3.png)

详细步骤如下：

**一 .** 攻击者首先通过getVaultReserve()函数获取了目前合约中的两个token地址。

**二 .** 通过transferfrom()函数给DLP合约分别转入13万FDO和115万FUSDT（攻击者地址之前的几笔交易已对资金进行approve授权）。

**三 .** 接下来进行闪电贷，攻击者通过flashLoan()函数进行闪电贷，得到13万枚wCRES和113万枚USDT。

以上操作均没有问题，攻击者对传入的币种进行闪电贷，获取贷款的资产。

那么问题出在哪？继续来看攻击者进行闪电贷的后续操作：

**四 .** 攻击者调用init()函数将自己的空气币FDO和FUSDT地址作为baseTokenAddress和quoteTokenAddress参数传入，也就是之前贷款的两个token地址wCRES和USDT。

问题就出在这里，正常情况下init()函数是在合约部署初始化时调用，那么这里为什么攻击者能够成功调用，接下来分析init()函数的合约代码怎么写的：

[![](https://p4.ssl.qhimg.com/t01fff3778f79b51853.png)](https://p4.ssl.qhimg.com/t01fff3778f79b51853.png)

上图中可以看到DVM合约中，存在init()函数对池子进行初始化设置操作，但该函数并不是只调用一次，也不是只有内部调用的internal属性，而是external属性，就是说可以进行外部调用。那么攻击者可以调用该函数就不奇怪了。

我们继续分析，攻击者将init()的token地址重新传入自己的空气币FDO和FUSDT地址有什么好处。

由于在之前的操作中，攻击者将这两种空气币（13万FDO和115万FUSDT）转入被攻击合约，之后进行闪电贷获取了贷款（13万枚wCRES和113万枚USDT），在闪电贷的操作中又重新调用被攻击合约的init()函数，并在之前合约token地址（wCRES和USDT ）处，传入两种空气币（FDO和FUSDT）的token地址，这里就是问题所在。

由于攻击者进行闪电贷时传入了空气币FDO和FUSDT，借走CRES和USDT，当原始的CRES和USDT地址修改成空气币FDO和FUSDT地址，攻击者还款时就还的是空气币FDO和FUSDT，也就达成了攻击者使用空气币借款并还款的目的。最终盗走13万枚wCRES和113万枚USDT，资金流转交易如下图：

[![](https://p2.ssl.qhimg.com/t0193d76b3a03a4466e.png)](https://p2.ssl.qhimg.com/t0193d76b3a03a4466e.png)



## 总结

该攻击事件中，主要利用DODO合约中可重新初始化漏洞，盗取了13万枚wCRES和113万枚USDT的巨额资产。这类问题主要是智能合约开发人员对函数调用没有进行严格校验，导致init()函数可重新调用。在零时科技安全团队审计过程中也曾出现过此类重复调用问题，并及时和项目方人员对接，规避了此类问题的发生。



## 安全建议

DeFi今年确实备受关注，黑客攻击也不断发生，包括Harvest Finance，Value DeFi，Akropolis，Cheese Bank和Origin Dollar等均受到不同程度的黑客攻击。针对频频发生的黑客攻击事件，我们给出以下的安全建议：

在项目上线之前，找专业的第三方安全企业进行全面的安全审计，而且可以找多家进行交叉审计；

可以发布漏洞赏金计划，发送社区白帽子帮助找问题，先于黑客找到漏洞；

加强对项目的安全监测和预警，尽量做到在黑客发动攻击之前发布预警从而保护项目安全。
