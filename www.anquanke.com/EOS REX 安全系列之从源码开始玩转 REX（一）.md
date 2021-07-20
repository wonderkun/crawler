> 原文链接: https://www.anquanke.com//post/id/177789 


# EOS REX 安全系列之从源码开始玩转 REX（一）


                                阅读量   
                                **158881**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t018fcf0dd059190513.jpg)](https://p2.ssl.qhimg.com/t018fcf0dd059190513.jpg)



## 前言

伴随着 REX 提案终于被 BP 们投票通过，炒了半年概念的 REX 终于上线了，这个号称稳赚不亏的投资项目吸引了众多人的目光，同时也霸占了各大区块链媒体的头条，其火热程度不亚于平台币，一上线便涌入了大量的资金。但是 REX 究竟是什么呢？REX 又有什么用？本系列基于 rex1.6.0-rc2 源码进行分析，给出相关的细节及答案。



## 什么是 REX

REX，全称 Resource Exchange，即资源交易所，是为了提供一个更好的资源租赁平台，缓解 EOS 高昂的资源使用成本，以更少的 EOS 换取更多的资源。同时也可以增加用户投票，促进 EOS 系统的良性运转。现在市面上有许多资源租赁 DApp，目的也是为了用于缓解 CPU 紧缺的问题。REX 与这些平台一样，都是充当租赁平台的角色，不同的是资源出租方不再是 DApp，而是每一个 EOS 持有者都能成为资源出租方，并享受收益。这里需要重点声明的是，REX 不是一种代币，而是一个资源租赁平台！用户购买的 REX 只是流转于 REX 租赁平台内的一种通证，用于证明用户出租了资源，这种通证本身不可流转，无法交易。类似于国债，REX 就是手中的债券。为了区分这两个概念，下文统一将 REX 资源租赁平台称为 REX。而用户购买得到的通证称为 rex。

更详细的资料可以参看 BM 自己的[文章](https://medium.com/@bytemaster/proposal-for-eos-resource-renting-rent-distribution-9afe8fb3883a)



## REX 攻略

对于一般用户而言，买卖 rex 只需要接触到以下几个接口，分别是：

1、depodit：用于充值，将 EOS 变成 SEOS，也叫预备金。

2、withdraw：用与提现，将 SEOS 换回 EOS。

3、buyrex：用于从用户的预备金中扣除相应的份额，并用于 rex 的购买。

4、sellrex：用于卖出已经结束锁定的 REX，并将本金连带收益一起放进用户的预备金账户中。

5、unstaketorex：将用于抵押中的资源用于 rex 的购买。

下面，我们一起来看下这几个函数的实现，了解资金的流向。



## deposit 函数

deposit 函数是用户参与 REX 的第一个接口，顾名思义，用户充值以备后来购买 rex。就像去游戏厅充值游戏币一样，先把人民币换成游戏厅的点数冲进卡里，然后用这张卡进行后续的游戏，后续的所有花费都是基于这张卡的。REX 也是相同的道理，后续所有的买卖操作都基于这个储备金账户。deposit 函数的具体实现如下：

```
void system_contract::deposit( const name&amp; owner, const asset&amp; amount )
   `{`
      require_auth( owner );

      check( amount.symbol == core_symbol(), "must deposit core token" );
      check( 0 &lt; amount.amount, "must deposit a positive amount" );
      INLINE_ACTION_SENDER(eosio::token, transfer)( token_account, `{` owner, active_permission `}`,
                                                    `{` owner, rex_account, amount, "deposit to REX fund" `}` );///充值进rex账户
      transfer_to_fund( owner, amount );///初始化用户余额，不存在用户则新增用户，存在则累加金额
      update_rex_account( owner, asset( 0, core_symbol() ), asset( 0, core_symbol() ) );
   `}`
```

我们不需要了解每一行的具体实现，但是大概的道理是需要明白的。deposit 函数做了以下事情：

1、首先在第三行校验了用户权限，总不能平白无故的让别人给自己买了 rex，绕过自己的意志。

2、在第五行和第六行对购买金额和代币的信息进行校验，不能拿假的 EOS 来买，也不能买个负数的，保证 REX 的安全性。

3、把用户的 EOS 打进 eosio.rex 账户，你的钱就从你的口袋，转到了 eosio.rex 系统账户上了。

4、调用 transfer_to_fund 接口，把用户的充值金额用小本本记起来，这相当我们的储备金钱包，在数据体现上是一个表，后续将根据这个表进行 rex 的购买。

5、调用 update_rex_account 接口，这个接口在输入不同的参数的时候有不同的功能，这里是用于处理用户的卖单，把用户卖 rex 得到的收益一并整理进储备金账户中。



## withdraw 函数

withdraw 函数是 deposit 函数的反向接口，用于将储备金账户中的余额转移到用户的 EOS 账户中，就像你在游戏厅玩够了，卡里还有点数，或玩游戏赢到点数放进卡里，就可以用卡里的点数换回人民币，下次再来，withdraw 函数的道理也是一样的。withdraw 函数的具体实现如下：

```
void system_contract::withdraw( const name&amp; owner, const asset&amp; amount )
   `{`
      require_auth( owner );

      check( amount.symbol == core_symbol(), "must withdraw core token" ); ///EOS符号校验
      check( 0 &lt; amount.amount, "must withdraw a positive amount" );
      update_rex_account( owner, asset( 0, core_symbol() ), asset( 0, core_symbol() ) );
      transfer_from_fund( owner, amount );
      INLINE_ACTION_SENDER(eosio::token, transfer)( token_account, `{` rex_account, active_permission `}`,
                                                    `{` rex_account, owner, amount, "withdraw from REX fund" `}` );
   `}`
```

与 deposit 函数大致一样，withdraw 函数同样对 EOS 代币的信息进行了相关的校验，与 deposit 函数不一样的是，withdraw 函数调用 update_rex_account 接口和 transfer_from_fund 接口的顺序与 deposit 函数不一样。但目的都是为了处理用户的 rex 卖单，将收益归结进储备金账户中。分别用于提现或购买 rex。这里详细的细节分析将放到后续文章之中。



## buyrex 函数

折腾了那么久，怎么充值看完了，怎么提现也看完了，下面就到了我们最关心的问题，就是该怎么买的问题了。买 rex 调用的接口为 buyrex 函数，函数的具体实现如下：

```
void system_contract::buyrex( const name&amp; from, const asset&amp; amount )
   `{`
      require_auth( from );

      check( amount.symbol == core_symbol(), "asset must be core token" );
      check( 0 &lt; amount.amount, "must use positive amount" );
      check_voting_requirement( from );//检查用户是否投票
      transfer_from_fund( from, amount ); //从用户的基金中扣除，需要先通过despoit函数进行充值之后才能进行rex的购买
      const asset rex_received    = add_to_rex_pool( amount ); //计算能获得的rex的数量
      const asset delta_rex_stake = add_to_rex_balance( from, amount, rex_received ); ///更改用户账户中的rex的数量
      runrex(2);
      update_rex_account( from, asset( 0, core_symbol() ), delta_rex_stake );
      // dummy action added so that amount of REX tokens purchased shows up in action trace 
      dispatch_inline( null_account, "buyresult"_n, `{` `}`, std::make_tuple( rex_received ) );      
   `}`
```

和前面两个函数一样，buyrex 函数同样也校验了代币的相关信息，然后使用 transfer_from_fund 函数从用户的储备金中扣除相应的金额。除此之外，我们还应该关注另外三个函数，分别是 check_voting_requirement，add_to_rex_pool 和 add_to_rex_balance。这三个函数分别用于检查用户是否投票、计算能购买到的 rex 的数量并把相应增加的 rex 数量加到 rexpool 中、记录用户购买的 rex 信息并计算用户购买的 rex 的解锁时间。那么，我们能获取到的 rex 的数量是怎么计算出来的呢？从源码上我们可以看到，计算 rex 的数量调用了 add_to_rex_pool 函数。所以，下面将着重分析 add_to_rex_pool 函数。



## add_to_rex_pool 函数

add_to_rex_pool 函数用于将用户购买的 rex 放进 rex_pool 中，并根据 rex_pool 中的相关信息计算出用户能够购买的 rex 的数量。首先我们先看下 rex_pool 表的定义：

```
struct [[eosio::table,eosio::contract("eosio.system")]] rex_pool `{`
      uint8_t    version = 0;
      asset      total_lent; /// total amount of CORE_SYMBOL in open rex_loans
      asset      total_unlent; /// total amount of CORE_SYMBOL available to be lent (connector) 
      asset      total_rent; /// fees received in exchange for lent  (connector)  
      asset      total_lendable; /// total amount of CORE_SYMBOL that have been lent (total_unlent + total_lent) 
      asset      total_rex; /// total number of REX shares allocated to contributors to total_lendable
      asset      namebid_proceeds; /// the amount of CORE_SYMBOL to be transferred from namebids to REX pool
      uint64_t   loan_num = 0; /// increments with each new loan

      uint64_t primary_key()const `{` return 0; `}`
   `}`;
```

以上是 rex_pool 表的定义，其中定义了 8 个字段，除去 version 参数，我们分别一个一个解释每个参数的意思

1、total_lent：用于记录总共被借出了多少的 cpu 资源和 net 资源，这个资源是以 EOS 为单位的。

2、total_unlent：记录 rex_pool 中未用于出借的 EOS 资源。包括用户因为购买 rex 所产生的可用于出租的金额，租用资源的用户的租金。 这其中有一部会因为出租资源而锁定的金额(30 天后自动解锁)，是一个 connector，用于 bancor 操作，计算一定数量的 EOS 可租借的资源。

3、total_rent：用于记录用户在租用资源的时候支付的租金，是一个 connector，其反应了租借资源的用户的多少。用于bancor操作，计算一定数量的 EOS 可租借的资源。

4、total_lenable:可以说是整个 rex_pool 的所有资金，计算公式为 total_unlent + total_lent。这里的资金来源还包括 name bid 的竞拍费用以及 ram fee。这个参数同时和用户的收益息息相关。

5、total_rex：rex_pool 中 rex 的总量，其来源于用户购买 rex。

6、namebid_proceeds：记录竞拍账户产生的费用。

7、loan_num：记录出租资源的总次数。

明白了以上字段的定义，我们现在正式看看 add_to_rex_pool 函数，以下是函数的具体实现。

```
asset system_contract::add_to_rex_pool( const asset&amp; payment )
   `{`
      /**
       * If CORE_SYMBOL is (EOS,4), maximum supply is 10^10 tokens (10 billion tokens), i.e., maximum amount
       * of indivisible units is 10^14. rex_ratio = 10^4 sets the upper bound on (REX,4) indivisible units to
       * 10^18 and that is within the maximum allowable amount field of asset type which is set to 2^62
       * (approximately 4.6 * 10^18). For a different CORE_SYMBOL, and in order for maximum (REX,4) amount not
       * to exceed that limit, maximum amount of indivisible units cannot be set to a value larger than 4 * 10^14.
       * If precision of CORE_SYMBOL is 4, that corresponds to a maximum supply of 40 billion tokens.
       */
      const int64_t rex_ratio       = 10000;
      const int64_t init_total_rent = 20'000'0000; /// base amount prevents renting profitably until at least a minimum number of core_symbol() is made available
      asset rex_received( 0, rex_symbol );
      auto itr = _rexpool.begin();
      if ( !rex_system_initialized() ) `{`
         /// initialize REX pool
         _rexpool.emplace( _self, [&amp;]( auto&amp; rp ) `{`
            rex_received.amount = payment.amount * rex_ratio; ///计算能获得的rex的数量
            rp.total_lendable   = payment;///由于用户 buy rex，使得 rex pool 中有可出租的 EOS，所以 rex_lendable 为首位用户的购买资金
            rp.total_lent       = asset( 0, core_symbol() );///初始化rex pool，暂时还没有人借资源
            rp.total_unlent     = rp.total_lendable - rp.total_lent; ///计算还能借的
            rp.total_rent       = asset( init_total_rent, core_symbol() );
            rp.total_rex        = rex_received;
            rp.namebid_proceeds = asset( 0, core_symbol() );
         `}`);
      `}` else if ( !rex_available() ) `{` /// should be a rare corner case, REX pool is initialized but empty
         _rexpool.modify( itr, same_payer, [&amp;]( auto&amp; rp ) `{`
            rex_received.amount      = payment.amount * rex_ratio;
            rp.total_lendable.amount = payment.amount;
            rp.total_lent.amount     = 0;
            rp.total_unlent.amount   = rp.total_lendable.amount - rp.total_lent.amount;
            rp.total_rent.amount     = init_total_rent;
            rp.total_rex.amount      = rex_received.amount;
         `}`);
      `}` else `{`
         /// total_lendable &gt; 0 if total_rex &gt; 0 except in a rare case and due to rounding errors
         check( itr-&gt;total_lendable.amount &gt; 0, "lendable REX pool is empty" );
         const int64_t S0 = itr-&gt;total_lendable.amount;
         const int64_t S1 = S0 + payment.amount;
         const int64_t R0 = itr-&gt;total_rex.amount;
         const int64_t R1 = (uint128_t(S1) * R0) / S0;
         rex_received.amount = R1 - R0; ///计算能获得的rex
         _rexpool.modify( itr, same_payer, [&amp;]( auto&amp; rp ) `{`
            rp.total_lendable.amount = S1;
            rp.total_rex.amount      = R1;
            rp.total_unlent.amount   = rp.total_lendable.amount - rp.total_lent.amount;
            check( rp.total_unlent.amount &gt;= 0, "programmer error, this should never go negative" );
         `}`);
      `}`

      return rex_received;
```

首先我们看下我们能购买到的 rex 是怎么计算的。当 rex_pool 迎来第一个购买 rex 的用户的时候，获得 rex 的获取比例是 1:10000，即 1 个 EOS 换 10000 个 rex，往后购买 rex 的用于按照公式((uint128_t(S1) R0) / S0) – R0计算能获取的 rex。看起来很复杂对不对？我们对公式进行分解下，首先进行以下转换，公式变为（S1 / S0 R0) – R0，再代入 S1，得到((S0 + payment) / S0 R0) – R0，最后我们进行分解再去括号，得到 R0 + (payment / S0) R0 – R0。最后这个公式就变成了(payment / S0) R0。再变一下，变成 payment (R0 / S0),即用户用于购买 rex 的资金乘以当前 rex_pool 中的 EOS 总资产与 rex_pool 中的 rex 的总量之间的比例。这个比例在没有第三方资金如账户竞拍费用，ram fee 等的干扰下是固定不变的，为 1:10000。但是当有第三方资金入场的时候，作为分母的 S0 就会不断变大，那么这个比例就不断变小，同样的金额能买到的 rex 就会越来越少。通过上面的分析，我们知道，在有第三方资金的参与下，rex 买得越早，能买到的数量就越多。rex 的价格与购买的人数无关，而与租借资源的数量，系统竞拍资源产生的收益，以及 ram fee有关。



## sellrex 函数

那么，现在流程走到这里，剩下的就是计算收益的问题了。用于处理用户出租 EOS 资源产生收益的计算细节的实现全部在 sellrex 函数中。以下是 sellrex 函数的具体实现。

```
void system_contract::sellrex( const name&amp; from, const asset&amp; rex )
   `{`
      require_auth( from );

      runrex(2);

      auto bitr = _rexbalance.require_find( from.value, "user must first buyrex" );
      check( rex.amount &gt; 0 &amp;&amp; rex.symbol == bitr-&gt;rex_balance.symbol,
             "asset must be a positive amount of (REX, 4)" );
      process_rex_maturities( bitr ); ///先收获成熟的rex
      check( rex.amount &lt;= bitr-&gt;matured_rex, "insufficient available rex" );///只能卖成熟的rex

      auto current_order = fill_rex_order( bitr, rex );///拿到出租EOS得到的分红
      asset pending_sell_order = update_rex_account( from, current_order.proceeds, current_order.stake_change );
      //订单状态不成功
      if ( !current_order.success ) `{`
         /**
          * REX order couldn't be filled and is added to queue.
          * If account already has an open order, requested rex is added to existing order.
          */
         auto oitr = _rexorders.find( from.value );
         if ( oitr == _rexorders.end() ) `{`
            oitr = _rexorders.emplace( from, [&amp;]( auto&amp; order ) `{`
               order.owner         = from;
               order.rex_requested = rex;
               order.is_open       = true;
               order.proceeds      = asset( 0, core_symbol() );
               order.stake_change  = asset( 0, core_symbol() );
               order.order_time    = current_time_point();
            `}`);
         `}` else `{`
            _rexorders.modify( oitr, same_payer, [&amp;]( auto&amp; order ) `{`
               order.rex_requested.amount += rex.amount;
            `}`);
         `}`
         pending_sell_order.amount = oitr-&gt;rex_requested.amount; 
      `}`
      check( pending_sell_order.amount &lt;= bitr-&gt;matured_rex, "insufficient funds for current and scheduled orders" );
      // dummy action added so that sell order proceeds show up in action trace
      if ( current_order.success ) `{`
         dispatch_inline( null_account, "sellresult"_n, `{` `}`, std::make_tuple( current_order.proceeds ) );
      `}`
   `}`
```

这个 sellrex 函数有很多学问，完整说下来可能不是这篇短短的分析能写完的，但是可以分析我们最关心的问题，就是获得的收益是怎么计算出来的。首先我们不管其他细节，先看看在真正计算收益之前做了什么。主要分为以下几步：

1、检查用户购买了 rex 没有，总不能没买就能卖对吧。

2、通过 process_rex_maturities 函数计算结束锁定的 rex，用户从购买的 rex 到卖 rex 需要 4 天的释放期。

3、检测需要卖出的 rex 的数量是否小于结束锁定的 REX 的数量。

通过以上几步检查之后，就真正进入了结算函数。rex 的收益结算是通过 fill_rex_order 接口实现的。看下具体实现



## fill_rex_order

```
rex_order_outcome system_contract::fill_rex_order( const rex_balance_table::const_iterator&amp; bitr, const asset&amp; rex )
   `{`
      auto rexitr = _rexpool.begin();
      const int64_t S0 = rexitr-&gt;total_lendable.amount;
      const int64_t R0 = rexitr-&gt;total_rex.amount;
      const int64_t p  = (uint128_t(rex.amount) * S0) / R0; ///越多人借资源收益越高
      const int64_t R1 = R0 - rex.amount; ///更新rex pool中rex的数量
      const int64_t S1 = S0 - p; ///更新rex pool中EOS的数量
      asset proceeds( p, core_symbol() ); ///获得的收益
      asset stake_change( 0, core_symbol() );
      bool  success = false; ///默认订单完成状态为0

      check( proceeds.amount &gt; 0, "proceeds are negligible" );

      const int64_t unlent_lower_bound = rexitr-&gt;total_lent.amount;
      //计算能未质押的rex pool中的EOS的数量，用于接下来观察是否足够支付用户产生的rex利润
      const int64_t available_unlent   = rexitr-&gt;total_unlent.amount - unlent_lower_bound; // available_unlent &lt;= 0 is possible 
      //rexpool中的钱足够支付rex利润
      if ( proceeds.amount &lt;= available_unlent ) `{`
         const int64_t init_vote_stake_amount = bitr-&gt;vote_stake.amount;
         const int64_t current_stake_value    = ( uint128_t(bitr-&gt;rex_balance.amount) * S0 ) / R0;
         _rexpool.modify( rexitr, same_payer, [&amp;]( auto&amp; rt ) `{`
            rt.total_rex.amount      = R1;///更新rex pool中的rex的数量
            rt.total_lendable.amount = S1; ///更新lenableEOS数量
            rt.total_unlent.amount   = rt.total_lendable.amount - rt.total_lent.amount; ///减少unlent数据
         `}`);
         //对用户的rexbalance账户进行操作
         _rexbalance.modify( bitr, same_payer, [&amp;]( auto&amp; rb ) `{`
            rb.vote_stake.amount   = current_stake_value - proceeds.amount;
            rb.rex_balance.amount -= rex.amount;
            rb.matured_rex        -= rex.amount; ///减少已经成熟的rex的数量
         `}`);
         stake_change.amount = bitr-&gt;vote_stake.amount - init_vote_stake_amount;
         success = true;
      ///不够钱支付的情况
      `}` else `{`
         proceeds.amount = 0;
      `}`

      return `{` success, proceeds, stake_change `}`;
   `}`
```

同样的，类似 add_to_rex_pool，我们也可以抛开其他细节，直击最核心的收益计算公式，即第 6 行的计算公式。（uint128_t(rex.amount) S0）/ R0，这个函数虽然看起来同样的复杂，但是我们可以用相同的方法进行简化。首先我们对公式进行一些转换，变成 rex.amount / R0 S0，加个括号，变成 rex.amount * (R0 / S0),即你能收益的 rex 是你要卖的 rex 乘以 rex_pool 中 rex 总量和 rex_pool 中得总 EOS 总资产之间的比例，这个比例在没有第三方资金如 name bid 和 ram fee 加入的情况下也是维持稳定不变的 10000:1。



## 我们知道了什么？

一口气说了一大堆，看到这里的你可能还有点茫然，可能只是记住了两个公式的转化，不打紧。我来总结下这次看完文章的的收获。通过以上的分析，我们知道买 rex 和卖 rex 都是根据 rex 总量和 rex_pool 中的 EOS 的总资金之间的比例进行计算的，也就是说在没有第三方资金参与，用户的 EOS 总是按 1:10000 的比例变成 rex，再按 10000:1 的比例再变成 EOS。这说明，在没有第三方资源的情况下，rex 和 EOS 总是按照一定的比例进行互换，这也是为什么 REX 号称稳赚不亏的原因。同时，在有第三方资金入场的时候，R0 / S0 的比例就会变小，也意味着 S0 / R0 的比例变大，虽然同样资金买到的 rex 变少了，但是，卖出去的比例就变大了，获得的收益就变得更多了。

整个参与的流程大致如下：

[![](https://p1.ssl.qhimg.com/t019b16a0a124ba7e29.jpg)](https://p1.ssl.qhimg.com/t019b16a0a124ba7e29.jpg)



## REX 安全性分析

REX 作为 EOS 本身的系统合约，其安全防护必须要做到面面俱到，一旦出现问题，将造成灾难性的影响。REX 合约已经由 EOS Authority 团队进行义务安全审计，但作为一名安全人员，笔者同时也对 REX 的整个架构进行了深入的思考，文章将会陆续对每个文章提及到的接口进行分析，阐述其安全性或安全性增强建议。

本文粗略介绍了四个接口，分别是deposit，withdraw，buyrex，sellrex。

从函数实现上来看：

1、每个函数都有对 asset 参数的信息进行校验，包括数量，代币的符号信息是否与系统代币信息一致。防止可能的假充值问题和溢出问题。

2、用户的关键操作都有权限校验，防止越权操作。

同时，文章内介绍的四个接口不存在 EOS 上常见的攻击手法如回滚攻击，排挤攻击，假通知攻击。

但值得注意的是，在这几个函数中，sellrex 函数曾存在一个严重漏洞(现已修复)，导致用于可以从 REX 中盗取资产。

详细信息如下：

[https://eosauthority.com/blog/REX_progress_with_testing_and_implementation_details](https://eosauthority.com/blog/REX_progress_with_testing_and_implementation_details)

漏洞的成因在于进行 sellrex 操作的时候 REX 系统可能会不够钱支付用户的收益，在这种情况下，用户的卖单就会挂起，如果没有校验订单，恶意用户就能在系统资金不足的情况下一直进行 sellrex 操作，一直增加挂起订单的金额，直到有系统有足够的资源支付用户的收益



## 结语

REX 是一个庞大的系统，不存在三言两语将全部细节分析到位情况，文章没有分析太多的技术细节，只是大概分析了每个函数的大概作用，介绍了关于 REX 收益最核心的地方。想要了解具体细节的朋友可以持续关注我们的系列文章～下一篇文章将会继续说明这些函数之间更加好玩的细节！文章可能有说得不对的地方，欢迎大家指点交流。



## 声明

本文仅用作技术参考，不构成任何投资建议。投资者应在充分了解相关风险的基础上进行理性投资。
