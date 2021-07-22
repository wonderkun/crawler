> 原文链接: https://www.anquanke.com//post/id/154409 


# 干货 | Solidity 安全：已知攻击方法和常见防御模式综合列表，Part-6


                                阅读量   
                                **138012**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者Dr Adrian Manning，文章来源：blog.sigmaprime.io
                                <br>原文地址：[https://blog.sigmaprime.io/solidity-security.html](https://blog.sigmaprime.io/solidity-security.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t013259bdd98ec81138.jpg)](https://p5.ssl.qhimg.com/t013259bdd98ec81138.jpg)

**翻译&amp;校对:** 爱上平顶山@慢雾安全团队 &amp; keywolf@慢雾安全团队<br>**致谢(校对)：**yudan、阿剑[@EthFans](https://github.com/EthFans)

> 本文由慢雾安全团队翻译，这里是最新译文的 GitHub 地址：[https://github.com/slowmist/Knowledge-Base/blob/master/solidity-security-comprehensive-list-of-known-attack-vectors-and-common-anti-patterns-chinese.md](https://github.com/slowmist/Knowledge-Base/blob/master/solidity-security-comprehensive-list-of-known-attack-vectors-and-common-anti-patterns-chinese.md)



## 一、拒绝服务

这个类别非常广泛，但其基本攻击形式都是让用户短暂地（在某些情形下，是永久）推出不可操作的合约。这种攻击可以把 Ether 永远锁在被攻击的合约中，正如 Parity 多签名钱包第二次被黑中的情形一样。

### 1.1 漏洞

有很多办法可以让合约变得不可操作。这里我只强调一些微妙的区块链 Solidity 编码模式，虽然看不太出来，但可能留下让攻击者执行 DOS 攻击的空间。

1.通过外部操纵映射或数组（Array）循环 ——在我的经历中，我看过此种模式的各种形式。通常情况下，它出现在 owner 希望在其投资者之间分配代币的情况下，以及，在合约中可以看到类似于 distribute() 函数的情况下：

```
contract DistributeTokens `{`
    address public owner; // gets set somewhere
    address[] investors; // array of investors
    uint[] investorTokens; // the amount of tokens each investor gets

    // ... extra functionality, including transfertoken()

    function invest() public payable `{`
        investors.push(msg.sender);
        investorTokens.push(msg.value * 5); // 5 times the wei sent
        `}`

    function distribute() public `{`
        require(msg.sender == owner); // only owner
        for(uint i = 0; i &lt; investors.length; i++) `{` 
            // here transferToken(to,amount) transfers "amount" of tokens to the address "to"
            transferToken(investors[i],investorTokens[i]); 
        `}`
    `}`
`}`
```

请注意，此合约中的循环遍历的数组可以被人为扩充。攻击者可以创建许多用户帐户，让 investor 数据变得更大。原则上来说，可以让执行 for 循环所需的 Gas 超过区块 Gas 上限，这会使 distribute() 函数变得无法操作。

2.所有者操作——另一种常见模式是所有者在合约中具有特定权限，并且必须执行一些任务才能使合约进入下一个状态。例如，ICO 合约要求所有者 finalize() 签订合约，然后才可以转让代币，即：

```
address public owner; // gets set somewhere

function finalize() public `{`
    require(msg.sender == owner);
    isFinalized == true;
`}`

// ... extra ICO functionality

// overloaded transfer function
function transfer(address _to, uint _value) returns (bool) `{`
    require(isFinalized);
    super.transfer(_to,_value)
`}`
```

在这种情况下，如果权限用户丢失其私钥或变为非活动状态，则整个代币合约就变得无法操作。在这种情况下，如果 owner 无法调用 finalize() 则代币不可转让；即代币系统的全部运作都取决于一个地址。

3.基于外部调用的进展状态——有时候，合约被编写成为了进入新的状态需要将 Ether 发送到某个地址，或者等待来自外部来源的某些输入。这些模式也可能导致 DOS 攻击：当外部调用失败时，或由于外部原因而被阻止时。在发送 Ether 的例子中，用户可以创建一个不接受 Ether 的合约。如果合约需要将 Ether 发送到这个地址才能进入新的状态，那么合约将永远不会达到新的状态，因为 Ether 永远不会被发送到合约。

### 1.2 预防技术

在第一个例子中，合约不应该遍历可以被外部用户人为操纵的数据结构。建议使用 withdrawal 模式，每个投资者都会调用取出函数独立取出代币。

在第二个例子中，改变合约的状态需要权限用户参与。在这样的例子中（只要有可能），如果 owner 已经瘫痪，可以使用自动防故障模式。一种解决方案是将 owner 设为一个多签名合约。另一种解决方案是使用一个时间锁，其中 [13]行 上的需求可以包括在基于时间的机制中，例如 require(msg.sender == owner || now &gt; unlockTime) ，那么在由 unlockTime 指定的一段时间后，任何用户都可以调用函数，完成合约。这种缓解技术也可以在第三个例子中使用。如果需要进行外部调用才能进入新状态，请考虑其可能的失败情况；并添加基于时间的状态进度，防止所需外部调用迟迟不到来。

注意：当然，这些建议都有中心化的替代方案，比如，可以添加 maintenanceUser ，它可以在有需要时出来解决基于 DOS 攻击向量的问题。通常，这类合约包含对这类权力实体的信任问题；不过这不是本节要探讨的内容。

### 1.3 真实的例子：GovernMental

GovernMental是一个很久以前的庞氏骗局，积累了相当多的 Ether。实际上，它曾经积累起 1100 个以太。不幸的是，它很容易受到本节提到的 DOS 漏洞的影响。这篇 Reddit 帖子描述了合约需要删除一个大的映射来取出以太。删除映射的 Gas 消耗量超过了当时的区块 Gas 上限，因此不可能撤回那 1100 个 Ether。合约地址为 0xF45717552f12Ef7cb65e95476F217Ea008167Ae3，您可以从交易0x0d80d67202bd9cb6773df8dd2020e7190a1b0793e8ec4fc105257e8128f0506b中看到，最后有人通过使用 250 万 Gas的交易取出了 1100 Ether 。



## 二、操纵区块时间戳

区块时间戳历来被用于各种应用，例如随机数的函数（请参阅随机数误区以获取更多详细信息）、锁定一段时间的资金、以及各种基于时间变更状态的条件语句。矿工有能力稍微调整时间戳，如果在智能合约中错误地使用区块时间戳，可以证明这是相当危险的。

一些有用的参考资料是：Solidity Docs，以及这个 Stack Exchange 上的问题。

### 2.1 漏洞

block.timestamp 或者别名 now 可以由矿工操纵，如果他们有这样做的激励的话。让我们构建一个简单的、容易受到矿工的剥削的游戏，

roulette.sol ：

```
contract Roulette `{`
    uint public pastBlockTime; // Forces one bet per block

    constructor() public payable `{``}` // initially fund contract

    // fallback function used to make a bet
    function () public payable `{`
        require(msg.value == 10 ether); // must send 10 ether to play
        require(now != pastBlockTime); // only 1 transaction per block
        pastBlockTime = now;
        if(now % 15 == 0) `{` // winner
            msg.sender.transfer(this.balance);
        `}`
    `}`
`}`
```

这份合约是一个简单的彩票。每个区块都有一笔交易可以下注 10 Ether，获得机会赢取合约中的全部余额。这里的假设是， block.timestamp 的最后两位数字是均匀分布的。如果是这样，那么将有 1/15 的机会赢得这个彩票。

但是，正如我们所知，矿工可以根据自己的意愿调整时间戳。在这种特殊情况下，如果合约中有足够的 Ether，挖出某个区块的矿工将被激励选择一个 block.timestamp 或 now 对 15 取余为 0 的时间戳。在这样做的时候，他们可能会赢得这个合约中的 Ether 以及区块奖励。由于每个区块只允许一个人下注，所以这也容易受到抢先提交攻击。

在实践中，区块时间戳是单调递增的，所以矿工不能选择任意块时间戳（它们必须大于其祖先块）。区块时间也不能是未来值，因为这些块可能会被网络拒绝（节点不会验证其时间戳指向未来的块）。

### 2.2 预防技术

区块时间戳不应该用于熵源或产生随机数——也就是说，它们不应该是游戏判定胜负或改变重要状态（如果假定为随机）的决定性因素（无论是直接还是通过某些推导）。

时效性强的逻辑有时是必需的；即解锁合约（时间锁定），几周后完成 ICO 或到期强制执行。有时建议使用 block.number（参见 Solidity 文档）和平均区块时间来估计时间；即，10 秒的区块时间运行 1 周，约等于，60480 个区块。因此，指定区块编号来更改合约状态可能更安全，因为矿工无法轻松操纵区块编号。BAT ICO合约就采用这种策略。

如果合约不是特别关心矿工对区块时间戳的操纵，这可能是不必要的，但是在开发合约时应该注意这一点。

### 2.3 真实的例子：GovernMental

GovernMental 是一个很久以前的庞氏骗局，积累了相当多的 Ether。它也容易受到基于时间戳的攻击。合约会在一轮内支付给最后一个加入合约的玩家（需要加入至少一分钟）。因此，作为玩家的矿工可以调整时间戳（未来的时间，使其看起来像是一分钟过去了），以显示玩家加入已经超过一分钟（尽管现实中并非如此）。关于这方面的更多细节可以在 Tanya Bahrynovska 的 以太坊安全漏洞史 中找到。
