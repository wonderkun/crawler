> 原文链接: https://www.anquanke.com//post/id/217358 


# DeFi 项目 bZx-iToken 盗币事件分析


                                阅读量   
                                **110843**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01976f68d70788678e.png)](https://p0.ssl.qhimg.com/t01976f68d70788678e.png)



作者：昏鸦@知道创宇404区块链安全研究团队

## 发生了什么

iToken是bZx推出的一种代币，今天早些时候，bZx官方发推表示发现了一些iTokens的安全事件，随后有研究员对比iToken合约源码改动，指出其中存在安全问题，可被攻击用于薅羊毛。

[![](https://p1.ssl.qhimg.com/t0193d346d12bafd9c5.png)](https://p1.ssl.qhimg.com/t0193d346d12bafd9c5.png)



## 什么是iToken

iToken是bZx推出的类似iDAI、iUSDC的累积利息的代币，当持有时，其价值会不断上升。iToken代表了借贷池中的份额，该池会随借贷人支付利息而扩大。iToken同样能用于交易、用作抵押、或由开发人员组成结构化产品，又或者用于安全价值存储。



## 分析

根据推文指出的代码，问题存在于`_internalTransferFrom`函数中，未校验`from`与`to`地址是否不同。

[![](https://p2.ssl.qhimg.com/t0133bb83ca7ede5246.png)](https://p2.ssl.qhimg.com/t0133bb83ca7ede5246.png)

若传入的`from`与`to`地址相同，在前后两次更改余额时`balances[_to] = _balancesToNew`将覆盖`balances[_from] = _balancesFromNew`的结果，导致传入地址余额无代价增加。

```
uint256 _balancesFrom = balances[_from];
uint256 _balancesTo = balances[_to];

require(_to != address(0), "15");

uint256 _balancesFromNew = _balancesFrom.sub(_value, "16");
balances[_from] = _balancesFromNew;

uint256 _balancesToNew = _balancesTo.add(_value);
balances[_to] = _balancesToNew;//knownsec// 变量覆盖,当_from与_to相同时
```



## 漏洞复现

截取`transferFrom`与`_internalTransferFrom`函数作演示，测试合约代码如下：

```
pragma solidity ^0.5.0;

library SafeMath `{`

    function add(uint256 a, uint256 b) internal pure returns (uint256) `{`
        uint256 c = a + b;
        require(c &gt;= a, "SafeMath: addition overflow");

        return c;
    `}`

    function sub(uint256 a, uint256 b) internal pure returns (uint256) `{`
        return sub(a, b, "SafeMath: subtraction overflow");
    `}`

    function sub(uint256 a, uint256 b, string memory errorMessage) internal pure returns (uint256) `{`
        require(b &lt;= a, errorMessage);
        uint256 c = a - b;

        return c;
    `}`

    function mul(uint256 a, uint256 b) internal pure returns (uint256) `{`
        if (a == 0) `{`
            return 0;
        `}`

        uint256 c = a * b;
        require(c / a == b, "SafeMath: multiplication overflow");

        return c;
    `}`

    function div(uint256 a, uint256 b) internal pure returns (uint256) `{`
        return div(a, b, "SafeMath: division by zero");
    `}`

    function div(uint256 a, uint256 b, string memory errorMessage) internal pure returns (uint256) `{`
        require(b &gt; 0, errorMessage);
        uint256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold

        return c;
    `}`

    function mod(uint256 a, uint256 b) internal pure returns (uint256) `{`
        return mod(a, b, "SafeMath: modulo by zero");
    `}`

    function mod(uint256 a, uint256 b, string memory errorMessage) internal pure returns (uint256) `{`
        require(b != 0, errorMessage);
        return a % b;
    `}`
`}`

contract Test `{`
    using SafeMath for uint256;
    uint256 internal _totalSupply;
    mapping(address =&gt; mapping (address =&gt; uint256)) public allowed;
    mapping(address =&gt; uint256) internal balances;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 amount);

    constructor() public `{`
        _totalSupply = 1 * 10 ** 18;
        balances[msg.sender] = _totalSupply;
    `}`

    function totalSupply() external view returns (uint256) `{`
        return _totalSupply;
    `}`

    function balanceOf(address account) external view returns (uint256) `{`
        return balances[account];
    `}`

    function approve(address spender, uint256 amount) external returns (bool) `{`
        require(spender != address(0));
        allowed[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
    `}`

    function transferFrom(
        address _from,
        address _to,
        uint256 _value)
        external
        returns (bool)
    `{`
        return _internalTransferFrom(
            _from,
            _to,
            _value,
            allowed[_from][msg.sender]
            /*ProtocolLike(bZxContract).isLoanPool(msg.sender) ?
                uint256(-1) :
                allowed[_from][msg.sender]*/
        );
    `}`

    function _internalTransferFrom(
        address _from,
        address _to,
        uint256 _value,
        uint256 _allowanceAmount)
        internal
        returns (bool)
    `{`
        if (_allowanceAmount != uint256(-1)) `{`
            allowed[_from][msg.sender] = _allowanceAmount.sub(_value, "14");
        `}`

        uint256 _balancesFrom = balances[_from];
        uint256 _balancesTo = balances[_to];

        require(_to != address(0), "15");

        uint256 _balancesFromNew = _balancesFrom
            .sub(_value, "16");
        balances[_from] = _balancesFromNew;

        uint256 _balancesToNew = _balancesTo
            .add(_value);
        balances[_to] = _balancesToNew;//knownsec// 变量覆盖,当_from与_to一致时

        // handle checkpoint update
        // uint256 _currentPrice = tokenPrice();

        // _updateCheckpoints(
        //     _from,
        //     _balancesFrom,
        //     _balancesFromNew,
        //     _currentPrice
        // );
        // _updateCheckpoints(
        //     _to,
        //     _balancesTo,
        //     _balancesToNew,
        //     _currentPrice
        // );

        emit Transfer(_from, _to, _value);
        return true;
    `}`
`}`
```

remix部署调试，`0x1e9c2524Fd3976d8264D89E6918755939d738Ed5`部署合约，拥有代币总量，授权`0x28deb6CA32C274f7DabF2572116863f39b4E65D9`500代币额度

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d2fbdb8b59d9f8fc.png)

通过`0x28deb6CA32C274f7DabF2572116863f39b4E65D9`账户，调用`transferFrom`函数，`_from`与`_to`传入地址`0x1e9c2524Fd3976d8264D89E6918755939d738Ed5`，`_value`传入授权的500

最后查看`0x1e9c2524Fd3976d8264D89E6918755939d738Ed5`地址余额，已增加500额度，超出代币发行总量。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011b4dce05ca463d07.png)

**综上，恶意用户可创建小号，通过不断授权给小号一定额度，使用小号频繁为大号刷代币，增发大量代币薅羊毛。**



## 总结

针对本次事件，根本原因，**还是没做好上线前的代码审计工作**。由于区块链智能合约的特殊性，智能合约上线前务必做好完善的代码审计、风险分析的工作。

另外通过github搜索到其他项目也同样存在这个问题，务必提高警惕。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01dd8786f62f26ac57.png)

知道创宇提供规避因合约安全问题导致的财产损失，为区块链应用提供专属安全解决方案。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/bbd55d7f-3bdd-410b-b269-50d0fa82b3ed.png-w331s)

### <a class="reference-link" name="%E5%8F%82%E8%80%83"></a>参考

[https://bzx.network/blog/incident](https://bzx.network/blog/incident)

[https://twitter.com/k06a/status/1305223411615117322](https://twitter.com/k06a/status/1305223411615117322)
