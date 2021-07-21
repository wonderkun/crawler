> 原文链接: https://www.anquanke.com//post/id/203548 


# 去中心化金融平台Lendf.Me黑客攻击事件分析


                                阅读量   
                                **392439**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t013b46600058d7b7e4.jpg)](https://p3.ssl.qhimg.com/t013b46600058d7b7e4.jpg)



## 1. 背景

2020年4月19日，以太坊 DeFi 平台dForce的 Lendf.Me协议遭受重入漏洞攻击。目前损失约2500万美元。这是继4月18日Uniswap被黑客攻击损失1278枚ETH（价值约22万美元）之后又一DeFi安全事件。这两起攻击事件都是 Defi 应用与 ERC777 标准组合不当导致的重入漏洞攻击。

DeFi是Decentralized Finance（去中心化金融）的缩写，也被称做Open Finance。DeFi希望借助于区块链的分布式、公开透明、不可篡改、可信等特点，建立点对点的金融，提供更加轻松便捷的金融服务。

dForce 开放式金融平台是著名的DeFi平台，Lendf.Me是由dForce主导开发的去中心化借贷市场协议。

imBTC 是与 BTC 1:1 锚定的 ERC-777 代币，由 Tokenlon 负责发行和监管，将 BTC 转账到 Tokenlon 的安全账户锁定，能够获得同等数量的 imBTC。imBTC是采用ERC77标准发行的代币。



## 2. 漏洞原理剖析

以太坊token最常见的标准是ERC-20标准，但也有ERC-223，ERC-721和ERC-777标准。ERC-777旨在改进ERC-20 token标准，并向后兼容。ERC777 定义了以下两个 hook 接口：

```
interface ERC777TokensSender `{`
    function tokensToSend(
        address operator,
        address from,
        address to,
        uint256 amount,
        bytes calldata userData,
        bytes calldata operatorData
    ) external;
`}`
```

```
interface ERC777TokensRecipient `{`
    function tokensReceived(
        address operator,
        address from,
        address to,
        uint256 amount,
        bytes calldata data,
        bytes calldata operatorData
    ) external;
`}`
```

ERC777 的转账实现一般类似下面这样：

```
function transfer(address to, uint256 amount) public returns (bool) `{`

  if (sender) `{`
      sender.tokensToSend(operator, from, to, amount, userData, operatorData);
  `}`

    _move(from, from, to, amount, "", "");

  if (Recipient) `{`
      Recipient.tokensReceived(operator, from, to, amount, userData, operatorData);
  `}`
  return true;
`}`
```

在 DeFi 合约调用 Token 的 transferFrom 时，Token 合约会调用 tokensToSend 和 tokenReceived 以便发送者和接收者进行相应的响应。这里 tokensToSend 由用户实现，tokenReceived 由 Defi 合约实现。在ERC777中，代币持有者可以通过 ERC1820 接口注册表合约注册自己的合约并通过在 tokensToSend这个钩子函数中定义一些操作来处理代币转账的过程中的某些流程。本次攻击实质就是攻击者利用DeFi平台处理不当构造了恶意的tokensToSend。



## 3. 攻击分析

攻击者地址：0xA9BF70A420d364e923C74448D9D817d3F2A77822。2020年4月19日12点43分，攻击者地址创建了攻击合约0x538359785a8d5ab1a741a0ba94f26a800759d91d。

[![](https://p2.ssl.qhimg.com/t015edda1de55dd827b.png)](https://p2.ssl.qhimg.com/t015edda1de55dd827b.png)

在etherscan上查看攻击合约地址的交易记录。发现前两条都是测试，从第三条开始攻击。

[![](https://p3.ssl.qhimg.com/t01ee260dd524de7056.png)](https://p3.ssl.qhimg.com/t01ee260dd524de7056.png)

选择 0xf8ed32d4a4aad0b5bb150f7a0d6e95b5d264d6da6c167029a20c098a90ff39b4这条交易来分析攻击过程。在下图中，可以看见，攻击者的合约地址向Lendf.Me存入0.00086375imBTC，取出的是存入的两倍。

[![](https://p5.ssl.qhimg.com/t013f2825291f14f149.png)](https://p5.ssl.qhimg.com/t013f2825291f14f149.png)

到bloxy.info上查看该交易 ，我们能知道完整的交易流程。如下图，有两个supply()函数，其中一个是存入0.00086375imBTC。下面一个supply()函数先存入0.00000001个imBTC，在transferFrom下的withdraw()函数提取了0.00172752imBTC

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018d67971092a0baee.png)

[![](https://p5.ssl.qhimg.com/t012d4f1de80e20af38.png)](https://p5.ssl.qhimg.com/t012d4f1de80e20af38.png)



## 4. 源码追踪分析

Lendf.Me合约地址：[https://etherscan.io/address/0x0eee3e3828a45f7601d5f54bf49bb01d1a9df5ea#code](https://etherscan.io/address/0x0eee3e3828a45f7601d5f54bf49bb01d1a9df5ea#code)

有四个关键点：1. 将用户当前余额存入临时变量。2. 调用了token的TransferFrom函数。3. 可以在supply()函数里调用withdraw() 4. TransferFrom函数调用之后更新存入临时变量的余额。supply函数源码参考附录。

1.supply()函数中，将用户当前余额存入临时变量。此处将用户余额存入到localResults.userSupplyUpdated。

[![](https://p0.ssl.qhimg.com/t0183b088858e7cdb46.png)](https://p0.ssl.qhimg.com/t0183b088858e7cdb46.png)

2.调用了token的TransferFrom函数。这里，同样是在supply函数中，第1583行，使用了doTransferIn()。

[![](https://p5.ssl.qhimg.com/t01ac7d7c45ee11a122.png)](https://p5.ssl.qhimg.com/t01ac7d7c45ee11a122.png)

追踪doTransferIn函数，发现调用了token的tansferFrom函数。

[![](https://p5.ssl.qhimg.com/t0116232cf0f1bf753b.png)](https://p5.ssl.qhimg.com/t0116232cf0f1bf753b.png)

由于黑客使用的是token是imBTC，于是找到imBTC合约中的transferFrom函数来分析。imBTC合约地址：[https://etherscan.io/address/0x3212b29E33587A00FB1C83346f5dBFA69A458923#code](https://etherscan.io/address/0x3212b29E33587A00FB1C83346f5dBFA69A458923#code)

imBTC的transferFrom代码如下图。这里callTokensToSend与callTokensReceived就是前面在ERC777协议里讲到的tokensToSend 和tokenReceived 。tokensToSend由用户实现，攻击者利用callTokensToSend的hook功能，调用了LendF.Me的withdraw()函数（由前面的bloxy.info分析知）

[![](https://p4.ssl.qhimg.com/t01f460fde9f429b100.png)](https://p4.ssl.qhimg.com/t01f460fde9f429b100.png)

3.可以在supply()函数里调用withdraw() 。withdraw()函数是用户用来取款的，攻击者构造了攻击合约，攻击合约利用ERC777钩子函数TokensToSend重入supply()调用withdraw()。withdraw()函数源码太多，参考附录。

4.前面说到supply()将用户当前余额存入临时变量，由于withdraw()重入supply，当withdrw()执行完时，攻击者余额已经为0，这时候再看supply()函数末尾，如下图，将之前临时变量localResults.userSupplyUpdated的的值拿来更新余额，这就是问题所在，本身余额已经是0，又将之前的余额写上，导致攻击者在取出全部余额后，余额任然不变。攻击者由此可以滚雪球一般盗取imBTC：假如攻击者原先余额为100，存入100，取出200后，账号还是200，攻击者再存入取出的200，取出400，再将取出的400存入，取出800……

[![](https://p4.ssl.qhimg.com/t01e7c304500b6e3f4b.png)](https://p4.ssl.qhimg.com/t01e7c304500b6e3f4b.png)



## 5. 攻击手法分析

**正常的存取流程**

正常用户是不会在supply()中重入withdraw()的

[![](https://p3.ssl.qhimg.com/t01447440970c298187.png)](https://p3.ssl.qhimg.com/t01447440970c298187.png)

**黑客攻击**

黑客通过部署合约利用TokensToSend将调用的withdraw()重入supply()。

[![](https://p0.ssl.qhimg.com/t01c01dfd2c758bd1c5.png)](https://p0.ssl.qhimg.com/t01c01dfd2c758bd1c5.png)



## 6. 修复
1. 给Supply函数和withdra()函数中加入 OpenZeppelin 的 ReentrancyGuard 函数，防止重入问题。


## 7. 关于Uniswap攻击事件

Uniswap攻击事件也是由于 DeFi平台和ERC777未做好兼容造成的。攻击方式与Lendf.Me本质是一样的，实现方式不一样而已。

### <a class="reference-link" name="%E9%99%84%E5%BD%95%EF%BC%9A"></a>附录：

**supply()函数**

```
function supply(address asset, uint amount) public returns (uint) `{`
    if (paused) `{`
        return fail(Error.CONTRACT_PAUSED, FailureInfo.SUPPLY_CONTRACT_PAUSED);
    `}`

    Market storage market = markets[asset];
    Balance storage balance = supplyBalances[msg.sender][asset];

    SupplyLocalVars memory localResults; // Holds all our uint calculation results
    Error err; // Re-used for every function call that includes an Error in its return value(s).
    uint rateCalculationResultCode; // Used for 2 interest rate calculation calls

    // Fail if market not supported
    if (!market.isSupported) `{`
        return fail(Error.MARKET_NOT_SUPPORTED, FailureInfo.SUPPLY_MARKET_NOT_SUPPORTED);
    `}`

    // Fail gracefully if asset is not approved or has insufficient balance
    err = checkTransferIn(asset, msg.sender, amount);
    if (err != Error.NO_ERROR) `{`
        return fail(err, FailureInfo.SUPPLY_TRANSFER_IN_NOT_POSSIBLE);
    `}`

    // We calculate the newSupplyIndex, user's supplyCurrent and supplyUpdated for the asset
    (err, localResults.newSupplyIndex) = calculateInterestIndex(market.supplyIndex, market.supplyRateMantissa, market.blockNumber, getBlockNumber());
    if (err != Error.NO_ERROR) `{`
        return fail(err, FailureInfo.SUPPLY_NEW_SUPPLY_INDEX_CALCULATION_FAILED);
    `}`

    (err, localResults.userSupplyCurrent) = calculateBalance(balance.principal, balance.interestIndex, localResults.newSupplyIndex);
    if (err != Error.NO_ERROR) `{`
        return fail(err, FailureInfo.SUPPLY_ACCUMULATED_BALANCE_CALCULATION_FAILED);
    `}`

    (err, localResults.userSupplyUpdated) = add(localResults.userSupplyCurrent, amount);
    if (err != Error.NO_ERROR) `{`
        return fail(err, FailureInfo.SUPPLY_NEW_TOTAL_BALANCE_CALCULATION_FAILED);
    `}`

    // We calculate the protocol's totalSupply by subtracting the user's prior checkpointed balance, adding user's updated supply
    (err, localResults.newTotalSupply) = addThenSub(market.totalSupply, localResults.userSupplyUpdated, balance.principal);
    if (err != Error.NO_ERROR) `{`
        return fail(err, FailureInfo.SUPPLY_NEW_TOTAL_SUPPLY_CALCULATION_FAILED);
    `}`

    // We need to calculate what the updated cash will be after we transfer in from user
    localResults.currentCash = getCash(asset);

    (err, localResults.updatedCash) = add(localResults.currentCash, amount);
    if (err != Error.NO_ERROR) `{`
        return fail(err, FailureInfo.SUPPLY_NEW_TOTAL_CASH_CALCULATION_FAILED);
    `}`

    // The utilization rate has changed! We calculate a new supply index and borrow index for the asset, and save it.
    (rateCalculationResultCode, localResults.newSupplyRateMantissa) = market.interestRateModel.getSupplyRate(asset, localResults.updatedCash, market.totalBorrows);
    if (rateCalculationResultCode != 0) `{`
        return failOpaque(FailureInfo.SUPPLY_NEW_SUPPLY_RATE_CALCULATION_FAILED, rateCalculationResultCode);
    `}`

    // We calculate the newBorrowIndex (we already had newSupplyIndex)
    (err, localResults.newBorrowIndex) = calculateInterestIndex(market.borrowIndex, market.borrowRateMantissa, market.blockNumber, getBlockNumber());
    if (err != Error.NO_ERROR) `{`
        return fail(err, FailureInfo.SUPPLY_NEW_BORROW_INDEX_CALCULATION_FAILED);
    `}`

    (rateCalculationResultCode, localResults.newBorrowRateMantissa) = market.interestRateModel.getBorrowRate(asset, localResults.updatedCash, market.totalBorrows);
    if (rateCalculationResultCode != 0) `{`
        return failOpaque(FailureInfo.SUPPLY_NEW_BORROW_RATE_CALCULATION_FAILED, rateCalculationResultCode);
    `}`

    /////////////////////////
    // EFFECTS &amp; INTERACTIONS
    // (No safe failures beyond this point)

    // We ERC-20 transfer the asset into the protocol (note: pre-conditions already checked above)
    err = doTransferIn(asset, msg.sender, amount);
    if (err != Error.NO_ERROR) `{`
        // This is safe since it's our first interaction and it didn't do anything if it failed
        return fail(err, FailureInfo.SUPPLY_TRANSFER_IN_FAILED);
    `}`

    // Save market updates
    market.blockNumber = getBlockNumber();
    market.totalSupply =  localResults.newTotalSupply;
    market.supplyRateMantissa = localResults.newSupplyRateMantissa;
    market.supplyIndex = localResults.newSupplyIndex;
    market.borrowRateMantissa = localResults.newBorrowRateMantissa;
    market.borrowIndex = localResults.newBorrowIndex;

    // Save user updates
    localResults.startingBalance = balance.principal; // save for use in `SupplyReceived` event
    balance.principal = localResults.userSupplyUpdated;
    balance.interestIndex = localResults.newSupplyIndex;

    emit SupplyReceived(msg.sender, asset, amount, localResults.startingBalance, localResults.userSupplyUpdated);

    return uint(Error.NO_ERROR); // success
`}`
```

**withdraw()函数**

```
function withdraw(address asset, uint requestedAmount) public returns (uint) `{`
    if (paused) `{`
        return fail(Error.CONTRACT_PAUSED, FailureInfo.WITHDRAW_CONTRACT_PAUSED);
    `}`

    Market storage market = markets[asset];
    Balance storage supplyBalance = supplyBalances[msg.sender][asset];

    WithdrawLocalVars memory localResults; // Holds all our calculation results
    Error err; // Re-used for every function call that includes an Error in its return value(s).
    uint rateCalculationResultCode; // Used for 2 interest rate calculation calls

    // We calculate the user's accountLiquidity and accountShortfall.
    (err, localResults.accountLiquidity, localResults.accountShortfall) = calculateAccountLiquidity(msg.sender);
    if (err != Error.NO_ERROR) `{`
        return fail(err, FailureInfo.WITHDRAW_ACCOUNT_LIQUIDITY_CALCULATION_FAILED);
    `}`

    // We calculate the newSupplyIndex, user's supplyCurrent and supplyUpdated for the asset
    (err, localResults.newSupplyIndex) = calculateInterestIndex(market.supplyIndex, market.supplyRateMantissa, market.blockNumber, getBlockNumber());
    if (err != Error.NO_ERROR) `{`
        return fail(err, FailureInfo.WITHDRAW_NEW_SUPPLY_INDEX_CALCULATION_FAILED);
    `}`

    (err, localResults.userSupplyCurrent) = calculateBalance(supplyBalance.principal, supplyBalance.interestIndex, localResults.newSupplyIndex);
    if (err != Error.NO_ERROR) `{`
        return fail(err, FailureInfo.WITHDRAW_ACCUMULATED_BALANCE_CALCULATION_FAILED);
    `}`

    // If the user specifies -1 amount to withdraw ("max"),  withdrawAmount =&gt; the lesser of withdrawCapacity and supplyCurrent
    if (requestedAmount == uint(-1)) `{`
        (err, localResults.withdrawCapacity) = getAssetAmountForValue(asset, localResults.accountLiquidity);
        if (err != Error.NO_ERROR) `{`
            return fail(err, FailureInfo.WITHDRAW_CAPACITY_CALCULATION_FAILED);
        `}`
        localResults.withdrawAmount = min(localResults.withdrawCapacity, localResults.userSupplyCurrent);
    `}` else `{`
        localResults.withdrawAmount = requestedAmount;
    `}`

    // From here on we should NOT use requestedAmount.

    // Fail gracefully if protocol has insufficient cash
    // If protocol has insufficient cash, the sub operation will underflow.
    localResults.currentCash = getCash(asset);
    (err, localResults.updatedCash) = sub(localResults.currentCash, localResults.withdrawAmount);
    if (err != Error.NO_ERROR) `{`
        return fail(Error.TOKEN_INSUFFICIENT_CASH, FailureInfo.WITHDRAW_TRANSFER_OUT_NOT_POSSIBLE);
    `}`

    // We check that the amount is less than or equal to supplyCurrent
    // If amount is greater than supplyCurrent, this will fail with Error.INTEGER_UNDERFLOW
    (err, localResults.userSupplyUpdated) = sub(localResults.userSupplyCurrent, localResults.withdrawAmount);
    if (err != Error.NO_ERROR) `{`
        return fail(Error.INSUFFICIENT_BALANCE, FailureInfo.WITHDRAW_NEW_TOTAL_BALANCE_CALCULATION_FAILED);
    `}`

    // Fail if customer already has a shortfall
    if (!isZeroExp(localResults.accountShortfall)) `{`
        return fail(Error.INSUFFICIENT_LIQUIDITY, FailureInfo.WITHDRAW_ACCOUNT_SHORTFALL_PRESENT);
    `}`

    // We want to know the user's withdrawCapacity, denominated in the asset
    // Customer's withdrawCapacity of asset is (accountLiquidity in Eth)/ (price of asset in Eth)
    // Equivalently, we calculate the eth value of the withdrawal amount and compare it directly to the accountLiquidity in Eth
    (err, localResults.ethValueOfWithdrawal) = getPriceForAssetAmount(asset, localResults.withdrawAmount); // amount * oraclePrice = ethValueOfWithdrawal
    if (err != Error.NO_ERROR) `{`
        return fail(err, FailureInfo.WITHDRAW_AMOUNT_VALUE_CALCULATION_FAILED);
    `}`

    // We check that the amount is less than withdrawCapacity (here), and less than or equal to supplyCurrent (below)
    if (lessThanExp(localResults.accountLiquidity, localResults.ethValueOfWithdrawal) ) `{`
        return fail(Error.INSUFFICIENT_LIQUIDITY, FailureInfo.WITHDRAW_AMOUNT_LIQUIDITY_SHORTFALL);
    `}`

    // We calculate the protocol's totalSupply by subtracting the user's prior checkpointed balance, adding user's updated supply.
    // Note that, even though the customer is withdrawing, if they've accumulated a lot of interest since their last
    // action, the updated balance *could* be higher than the prior checkpointed balance.
    (err, localResults.newTotalSupply) = addThenSub(market.totalSupply, localResults.userSupplyUpdated, supplyBalance.principal);
    if (err != Error.NO_ERROR) `{`
        return fail(err, FailureInfo.WITHDRAW_NEW_TOTAL_SUPPLY_CALCULATION_FAILED);
    `}`

    // The utilization rate has changed! We calculate a new supply index and borrow index for the asset, and save it.
    (rateCalculationResultCode, localResults.newSupplyRateMantissa) = market.interestRateModel.getSupplyRate(asset, localResults.updatedCash, market.totalBorrows);
    if (rateCalculationResultCode != 0) `{`
        return failOpaque(FailureInfo.WITHDRAW_NEW_SUPPLY_RATE_CALCULATION_FAILED, rateCalculationResultCode);
    `}`

    // We calculate the newBorrowIndex
    (err, localResults.newBorrowIndex) = calculateInterestIndex(market.borrowIndex, market.borrowRateMantissa, market.blockNumber, getBlockNumber());
    if (err != Error.NO_ERROR) `{`
        return fail(err, FailureInfo.WITHDRAW_NEW_BORROW_INDEX_CALCULATION_FAILED);
    `}`

    (rateCalculationResultCode, localResults.newBorrowRateMantissa) = market.interestRateModel.getBorrowRate(asset, localResults.updatedCash, market.totalBorrows);
    if (rateCalculationResultCode != 0) `{`
        return failOpaque(FailureInfo.WITHDRAW_NEW_BORROW_RATE_CALCULATION_FAILED, rateCalculationResultCode);
    `}`

    /////////////////////////
    // EFFECTS &amp; INTERACTIONS
    // (No safe failures beyond this point)

    // We ERC-20 transfer the asset into the protocol (note: pre-conditions already checked above)
    err = doTransferOut(asset, msg.sender, localResults.withdrawAmount);
    if (err != Error.NO_ERROR) `{`
        // This is safe since it's our first interaction and it didn't do anything if it failed
        return fail(err, FailureInfo.WITHDRAW_TRANSFER_OUT_FAILED);
    `}`

    // Save market updates
    market.blockNumber = getBlockNumber();
    market.totalSupply =  localResults.newTotalSupply;
    market.supplyRateMantissa = localResults.newSupplyRateMantissa;
    market.supplyIndex = localResults.newSupplyIndex;
    market.borrowRateMantissa = localResults.newBorrowRateMantissa;
    market.borrowIndex = localResults.newBorrowIndex;

    // Save user updates
    localResults.startingBalance = supplyBalance.principal; // save for use in `SupplyWithdrawn` event
    supplyBalance.principal = localResults.userSupplyUpdated;
    supplyBalance.interestIndex = localResults.newSupplyIndex;

    emit SupplyWithdrawn(msg.sender, asset, localResults.withdrawAmount, localResults.startingBalance, localResults.userSupplyUpdated);

    return uint(Error.NO_ERROR); // success
`}`
```



## 参考：
- [https://tokenlon.zendesk.com/hc/zh-cn/articles/360035113211-imBTC-%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98](https://tokenlon.zendesk.com/hc/zh-cn/articles/360035113211-imBTC-%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)
- [https://eips.ethereum.org/EIPS/eip-777](https://eips.ethereum.org/EIPS/eip-777)
- [https://mp.weixin.qq.com/s/2ElVUSrk-heV9mpFIwnDhg](https://mp.weixin.qq.com/s/2ElVUSrk-heV9mpFIwnDhg)
- [https://learnblockchain.cn/article/893](https://learnblockchain.cn/article/893)
- [https://www.8btc.com/media/584740](https://www.8btc.com/media/584740)
- [https://www.8btc.com/media/584802](https://www.8btc.com/media/584802)
- <a>https://medium.com/@peckshield/uniswap-lendf-me-hacks-root-cause-and-loss-analysis-50f3263dcc09</a>