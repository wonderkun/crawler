> 原文链接: https://www.anquanke.com//post/id/173089 


# EOS新型攻击手法之 hard_fail 状态攻击


                                阅读量   
                                **181839**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t01aef440d7a2fff20a.jpg)](https://p5.ssl.qhimg.com/t01aef440d7a2fff20a.jpg)



by yudan@慢雾安全团队

## 前言

昨日（2019 年 3 月 10 日）凌晨，EOS游戏 Vegas Town（合约帐号 eosvegasgame）遭受攻击，损失数千 EOS。慢雾安全团队及时捕获这笔攻击，并同步给相关的交易所及项目方。本次攻击手法之前没有相同的案例，但可以归为假充值类别中的一种。对此慢雾安全团队进行了深入的分析。



## 攻击回顾

根据慢雾安全团队的持续分析，本次的攻击帐号为 fortherest12，通过 eosq 查询该帐号，发现首页存在大量的错误执行交易：

[![](https://p2.ssl.qhimg.com/t01bd5457dd35ff4675.jpg)](https://p2.ssl.qhimg.com/t01bd5457dd35ff4675.jpg)

查看其中任意一笔交易，可以发现其中的失败类型均为 hard_fail：

[![](https://p5.ssl.qhimg.com/t01e6c02bc2e95036e5.jpg)](https://p5.ssl.qhimg.com/t01e6c02bc2e95036e5.jpg)

这立即就让我想起了不久前的写过的一篇关于 EOS 黑名单攻击手法的分析，不同的是实现攻击的手法，但是原理是类似的，就是没有对下注交易的状态进行分析。



## 攻击分析

本次攻击的一个最主要的点有两个，一个是 hard_fail，第二个是上图中的延迟。可以看到的是上图中的延迟竟达到了 2 个小时之久。接下来我们将对每一个要点进行分析。

(1)hard_faild：

参考官方开发文档（[https://developers.eos.io/eosio-nodeos/docs/how-to-monitor-state-with-state-history-plugin）](https://developers.eos.io/eosio-nodeos/docs/how-to-monitor-state-with-state-history-plugin%EF%BC%89)

[![](https://p5.ssl.qhimg.com/t0111dc1ad18520b777.jpg)](https://p5.ssl.qhimg.com/t0111dc1ad18520b777.jpg)

可以得知 fail 有两种类型，分别是 soft_fail 和 hard_fail，soft_fail 我们遇见的比较多，我们一般自己遇到合约内执行 eosio_assert 的时候就会触发 soft_fail，回看官方对 soft_fail 的描述：客观的错误并且错误处理器正确执行，怎么说呢？拿合约内 eosio_assert 的例子来说：

```
`{`
  //do something
  eosio_assert(0,"This is assert by myself");
  //do others
`}`
```

这种用户自己的错误属于客观错误，并且当发生错误之后，错误处理器正确执行，后面提示的内容 This is assert by myself 就是错误处理器打印出来的消息。<br>
那么 hard_fail 是什么呢？回看官方对 hard_fail 的描述：客观的错误并且错误处理器没有正确执行。那又是什么意思呢？简单来说就是出现错误但是没有使用错误处理器（error handler）处理错误，比方说使用 onerror 捕获处理，如果说没有 onerror 捕获，就会 hard_fail。

OK，到这里，我们已经明白了 hard_fail 和 soft_fail 的区别，接下来是怎么执行的问题，传统的错误抛出都是使用 eosio_assert 进行抛出的，自然遇到 hard_fail 机会不多，那怎么抛出一个 hard_fail 错误呢？我们继续关注下一个点—-延迟时间。

(2)延迟时间：

很多人可能会疑惑，为什么会有延迟时间，我们通过观察可以知道 fortherest12 是一个普通帐号，我们惯常知道的延时交易都是通过合约发出的，其实通过 cleos 中的一个参数设置就可以对交易进行延迟，即使是非合约帐号也可以执行延迟交易，但是这种交易不同于我们合约发出的 eosio_assert，没有错误处理，根据官方文档的描述，自然会变成 hard_fail。而且最关键的一个点是，hard_fail 会在链上出现记录。



## 攻击细节分析

根据 jerry[@EOSLive](https://github.com/EOSLive) 钱包的讲解，本次的攻击发生和 EOS 的机制相关，当交易的延迟时间不为 0 的时候，不会立马校验是否执行成功，对延迟交易的处理是 push_schedule_transaction，而交易的延迟时间等于 0 的时候，会直接 push_transaction。这两个的处理机制是存在区别的。



## 攻击成因

本次攻击是因为项目方没有对 trx 的 status 状态进行校验，只是对 trx 是否存在作出了判断。从而导致了本次攻击的发生。



## 防御手法

项目方在进行线下开奖的时候，要注意下注订单的执行状态，不要只是判断交易是否存在，还要判断下注订单是否成功执行。如下图

[![](https://p3.ssl.qhimg.com/t015e455f3e445f34cb.jpg)](https://p3.ssl.qhimg.com/t015e455f3e445f34cb.jpg)



## 相关参考

引起 object fail 的错误类型参考：[https://eos.live/detail/16715](https://eos.live/detail/16715)

官方对交易执行状态的描述：[https://developers.eos.io/eosio-nodeos/docs/how-to-monitor-state-with-state-history-plugin](https://developers.eos.io/eosio-nodeos/docs/how-to-monitor-state-with-state-history-plugin)
