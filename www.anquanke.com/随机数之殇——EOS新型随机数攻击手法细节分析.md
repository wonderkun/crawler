> 原文链接: https://www.anquanke.com//post/id/187423 


# 随机数之殇——EOS新型随机数攻击手法细节分析


                                阅读量   
                                **534128**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01a98b0773aa6f2658.jpg)](https://p5.ssl.qhimg.com/t01a98b0773aa6f2658.jpg)

> by yudan@慢雾安全团队 &amp; Jerry[@EOS](https://github.com/EOS) Live 钱包
本篇攻击手法技术分析基于 EOS 1.8 以前版本，在新版本中未做测试。

## 0x01 事件回顾

根据慢雾区情报，EOS DApp EOSPlay 中的 DICE 游戏于9月14日晚遭受新型随机数攻击，损失金额高达数万 EOS。经过慢雾安全团队的分析，发现攻击者（账号：muma******mm）在此次攻击过程中利用 EOS 中的经济模型的缺陷，使用了一种新型的随机数攻击手法对项目方进行攻击。

在开始详细的细节剖析之前，需要先了解一些技术背景作为铺垫。



## 0x02 技术背景

我们知道，在 EOS 系统中，资源是保证整个 EOS 系统安全运行的关键，在 EOS 上发出的每一笔交易都要消耗对应的资源，如 CPU、NET 或 RAM，而这些资源都是需要一定量的 EOS 作为抵押换取的，如果抵押的 EOS 的数量不够，则无法换取足够的资源发起交易。而本次的攻击行为则是利用了 EOS 资源里面的 CPU 资源模型进行攻击。我们知道，在 EOS 上 CPU 是一个十分重要，也是消耗最多的资源。在 EOS DApp 活跃的时候，会经常出现 CPU 不足的情况，为此，还催生出许多做 CPU 抵押的第三方 DApp，缓解资源使用紧张的问题。那么 CPU 资源的份额具体是怎么计算的呢？<br>
参考 [MEETONE 的文章](https://github.com/meet-one/documentation/blob/master/docs/EOSIO-CPU.md) 我们可以看到 CPU 的计算方式为

```
max_block_cpu_usage * (account_cpu_usage_average_window_ms / block_interval_ms) * your_staked_cpu_count / total_cpu_count
```

其中，`max_block_cpu_usage * (account_cpu_usage_average_window_ms / block_interval_ms)` 是一个固定的变量，也就是常量。那么真正影响帐号的 CPU 使用情况的是后面的公式 `your_staked_cpu_count / total_cpu_count`，这里的意思就是，你抵押的 CPU 总量除以总的 CPU 抵押总量，那么，如果总量变多了，如果你的抵押数量没跟上去，能用的 CPU 就会变得越来越少。而 CPU 不足，则无法正常地发起交易。在了解完 CPU 的相关知识后，就可以开始相关的分析了。



## 0x03 攻击细节剖析

本次的攻击帐号为 muma******mm,通过分析该帐号行为，发现该帐号通过 start 操作发送了大量的 defer 交易，这些 defer 操作里面又发起了另一个 start 操作，然后无限循环下去。

[![](https://p0.ssl.qhimg.com/t0166a917ae75cd767f.jpg)](https://p0.ssl.qhimg.com/t0166a917ae75cd767f.jpg)

由于这些大量的交易充斥着区块，为分析工作带来了困难，所以首先要对这些交易进行筛选。查看攻击者帐号的接收开奖通知的交易，通过查询游戏的开奖区块，我们发现一个问题，就是在多个开奖区块内只有系统的 onblock 一笔交易，说明这个区块为空块。很明显，这是因为 CPU 价格的太高导致交易无法发出而出现的情况。而本次受攻击的 EOS Play 采用的是使用未来区块哈希进行开奖。

[![](https://p4.ssl.qhimg.com/t01b06faf9b79d9acbc.jpg)](https://p4.ssl.qhimg.com/t01b06faf9b79d9acbc.jpg)

那么攻击者为什么要选择这样做呢？我们来分析下区块哈希的计算方法

[![](https://p1.ssl.qhimg.com/t01e01b4a6b9b01b821.jpg)](https://p1.ssl.qhimg.com/t01e01b4a6b9b01b821.jpg)

通过上图我们可以看到，区块哈希的计算最终调用了 digest() 方法，而 digest() 方法的实现为对 block_header 结构体本身进行哈希。我们继续看 block_header 的定义

[![](https://p2.ssl.qhimg.com/t011e723294e0ea825c.jpg)](https://p2.ssl.qhimg.com/t011e723294e0ea825c.jpg)

可以看到 block_header 结构体的变量分别有<br>
1、confrimed<br>
2、previous<br>
3、transaction_mroot<br>
4、action_mroot<br>
5、schedule_version<br>
6、new_producers<br>
7、header_extensions

其代表的含义分别为<br>
1、每一轮开始前需要确认的上一轮生产的区块数<br>
2、之前区块的区块哈希<br>
3、区块 transaction 的默克尔根哈希<br>
4、区块 action 的默克尔根哈希<br>
5、节点出块顺序表版本，这个在一段时间内是不会改变的<br>
6、新的出块节点，可为空<br>
7、拓展，1.8 之前这个变量为空

到了这里，我们可以清楚的看到，除了 action_mroot 和 transaction_mroot 外，所有的其他变量都是可以轻松获取的，然后我们继续深入看下 transaction_mroot 和 action_mroot 的计算方法。

[![](https://p3.ssl.qhimg.com/t0124d7c701a701686f.jpg)](https://p3.ssl.qhimg.com/t0124d7c701a701686f.jpg)

可以看到 transaction_mroot 和 action_mroot 是分别对 pending_block 内的 action 和 transaction 的总的 digests 进行一个 merkle 运算最终得到一个 transaction_mroot 和 action_mroot。我们继续追踪各自的 digest 的生成方式

[![](https://p4.ssl.qhimg.com/t01457a360211262a24.jpg)](https://p4.ssl.qhimg.com/t01457a360211262a24.jpg)

[![](https://p1.ssl.qhimg.com/t019c71651ba74582bb.jpg)](https://p1.ssl.qhimg.com/t019c71651ba74582bb.jpg)

以上两条分别是 transaction digest 和 action digest 的生成方式，我们可以看到，transsaction digest 的计算使用到了 cpu 和 net 作为因子，这两个因子取决于交易执行时 bp 的节点状态，虽然透明但较难准确预测，而 action digest 没有使用到这两个变量，可以轻松的算出来。那么分析到这里，我们可以确定的是，要预测一个区块的哈希，需要引入不确定的 cpu 和 net 的使用量，那么，有没有办法不将这两个因子引入到计算当中呢？

**答案是必然的！**

我们把目光聚集到项目方开奖区块的唯一一个交易 onblock 中，首先我们先看看 onblock 的生成定义

[![](https://p2.ssl.qhimg.com/t012c487a6b9a3790bd.jpg)](https://p2.ssl.qhimg.com/t012c487a6b9a3790bd.jpg)

以上是构造 onblock 操作的一些定义，可以看到，onblock 操作的 data 字段为 header_block_header，就是当前的区块头信息，即相对于当前 pending 区块上一个块的区块信息，接下来我们追踪该函数的调用过程。

[![](https://p0.ssl.qhimg.com/t0115a2b49b27a62dcb.jpg)](https://p0.ssl.qhimg.com/t0115a2b49b27a62dcb.jpg)

发现一个点，就是这里会把 onblock 交易的 implict 设置为 true，这样设置有什么用效果呢? 我们接下来看下交易的打包过程

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01183ec1033de32138.jpg)

这里看到，由于在区块开始的时候，implict 属性被设置为 true，导致交易在被打包时 onblock 交易不会进入 pending 区块的 transaction 序列中，但是却进入了 pending 区块的 action 序列。也就是说，项目方的开奖区块的 action 序列不为空，而 transaction 序列为空。所以说开奖区块的 transaction_mroot 必然为 0，这样，就避开了计算 transaction_mroot 时引入的 cpu 和 net 这些不确定因素，只计算 action_mroot 即可。而 action_mroot 的计算只需要对 onblock action 本身进行计算即可，且 onblock 的 data 是可以拿到的，即当前区块头信息，也就是相对于当前 pending 区块的上一个区块的信息。那么到了这里，攻击者已经完全可以拿到可计算开奖区块哈希 的所有信息，计算出开奖区块哈希 就不是什么难事了。



## 0x04 攻击情况总结

在完成攻击细节剖析后，我们可以知道，攻击者在下注时，并不知道开奖区块的区块哈希，因为该哈希和开奖区块的前一个块相关，所以攻击者能做的是在开奖区块的前一个块对开奖区块的信息进行计算。那万一计算不对怎么办呢？关于这点，我们发现一个现象，当区块计算结果和预期有误差时，攻击者会在开奖区块发送一笔 hi 交易来企图改变结果，但是由于新引入的 hi 交易会引入 cpu 和 net 使用量这些变量，所以引入 hi 交易并不能确保结果可控，但是已经将赢的概率大大提升了，相当于重新开奖。

[![](https://p1.ssl.qhimg.com/t0170e9d41112e7299e.jpg)](https://p1.ssl.qhimg.com/t0170e9d41112e7299e.jpg)

总结下来攻击者的攻击手法为：<br>
1、通过 REX 购买大量的 CPU，导致正常交易无法发出<br>
2、在假设开奖区块为空块的情况下对开奖区块的哈希进行计算<br>
3、当发现计算结果不对时，向开奖区块内发送一笔 hi 交易，尝试改变结果。



## 0x05 预防方案

EOS Play 由于使用了未来区块哈希作为开奖因子，导致开奖结果被预测从而导致攻击发生。这次的例子再一次的告诉我们，所有使用区块信息进行开奖的开奖方案都是不成熟的，都存在被预测的可能。特别是 REX 出现以后，抬高 CPU 价格比以往变得更为容易。

慢雾安全团队在此提醒，DApp 项目方在使用随机数时，特别是涉及到关键操作的随机数，应尽量采用更为安全的线下随机数生成方案，降低随机数被攻击的风险。除此之外，同时还可以接入慢雾安全团队孵化的 EOS 智能合约防火墙 FireWall.X（[https://firewallx.io](https://firewallx.io)），为合约安全保驾护航。
