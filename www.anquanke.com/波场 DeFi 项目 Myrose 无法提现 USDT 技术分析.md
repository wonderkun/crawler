> 原文链接: https://www.anquanke.com//post/id/217601 


# 波场 DeFi 项目 Myrose 无法提现 USDT 技术分析


                                阅读量   
                                **104658**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t017007f78cc904f692.jpg)](https://p4.ssl.qhimg.com/t017007f78cc904f692.jpg)



作者：昏鸦,Al1ex@知道创宇404区块链安全研究团队

## 事件起因

2020年9月14日晚20:00点，未经安全审计的波场最新Defi项目Myrose.finance登陆Tokenpocket钱包，首批支持JST、USDT、SUN、DACC挖矿，并将逐步开通ZEUS、PEARL、CRT等的挖矿，整个挖矿周期将共计产出8400枚ROSE，预计将分发给至少3000名矿工，ROSE定位于波场DeFi领域的基础资产，不断为持有者创造经济价值。

项目上线之后引来了众多的用户(高达5700多人)参与挖矿，好景不长，在20:09左右有用户在Telegram”Rose中文社区群”中发文表示USDT无法提现：

[![](https://p2.ssl.qhimg.com/t01bb5bd2ae6231e45a.png)](https://p2.ssl.qhimg.com/t01bb5bd2ae6231e45a.png)

截止发文为止，无法提现的USDT数量高达6,997,184.377651 USDT(约700万USDT)，随后官方下线USDT挖矿项目。

[https://tronscan.io/#/contract/TM9797VRM66LyKXq2TbxP1sNmuQWBrsnYw/token-balances](https://tronscan.io/#/contract/TM9797VRM66LyKXq2TbxP1sNmuQWBrsnYw/token-balances)

[![](https://p0.ssl.qhimg.com/t01ac860a8c606a01ca.png)](https://p0.ssl.qhimg.com/t01ac860a8c606a01ca.png)



## 分析复现

我们直接通过模拟合约在remix上测试。

USDT模拟测试合约代码如下，USDT_Ethereum和USDT_Tron分别模拟两个不同平台的USDT代币合约，分别代表`transfer`函数有显式`return true`和无显式`return true`

```
pragma solidity ^0.5.0;

import "IERC20.sol";
import "SafeMath.sol";

contract USDT_Ethereum is IERC20 `{`
    using SafeMath for uint256;

    uint256 internal _totalSupply;

    mapping(address =&gt; uint256) internal _balances;
    mapping (address =&gt; mapping (address =&gt; uint)) private _allowances;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint value);

    constructor() public `{`
        _totalSupply = 1 * 10 ** 18;
        _balances[msg.sender] = _totalSupply;
    `}`

    function totalSupply() external view returns (uint256) `{`
        return _totalSupply;
    `}`
    function balanceOf(address account) external view returns (uint256) `{`
        return _balances[account];
    `}`
    function allowance(address owner, address spender) external view returns (uint256) `{`
        return _allowances[owner][spender];
    `}`
    function approve(address spender, uint amount) public returns (bool) `{`
        _approve(msg.sender, spender, amount);
        return true;
    `}`
    function _approve(address owner, address spender, uint amount) internal `{`
        require(owner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");

        _allowances[owner][spender] = amount;
        emit Approval(owner, spender, amount);
    `}`
    function mint(address account, uint amount) external `{`
        require(account != address(0), "ERC20: mint to the zero address");

        _totalSupply = _totalSupply.add(amount);
        _balances[account] = _balances[account].add(amount);
        emit Transfer(address(0), account, amount);
    `}`

    function _transfer(address _from ,address _to, uint256 _value) internal returns (bool) `{`
        require(_to != address(0));
        require(_value &lt;= _balances[msg.sender]);

        _balances[_from] = _balances[_from].sub(_value, "ERC20: transfer amount exceeds balance");
        _balances[_to] = _balances[_to].add(_value);
        emit Transfer(_from, _to, _value);
        return true;
    `}`
    function transfer(address to, uint value) public returns (bool) `{`
        _transfer(msg.sender, to, value);
        return true;//显式return true
    `}`
    function transferFrom(address from, address to, uint value) public returns (bool) `{`
        _transfer(from, to, value);
        _approve(from, msg.sender, _allowances[from][msg.sender].sub(value, "ERC20: transfer amount exceeds allowance"));
        return true;
    `}`
`}`

contract USDT_Tron is IERC20 `{`
    using SafeMath for uint256;

    uint256 internal _totalSupply;

    mapping(address =&gt; uint256) internal _balances;
    mapping (address =&gt; mapping (address =&gt; uint)) private _allowances;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint value);

    constructor() public `{`
        _totalSupply = 1 * 10 ** 18;
        _balances[msg.sender] = _totalSupply;
    `}`

    function totalSupply() external view returns (uint256) `{`
        return _totalSupply;
    `}`
    function balanceOf(address account) external view returns (uint256) `{`
        return _balances[account];
    `}`
    function allowance(address owner, address spender) external view returns (uint256) `{`
        return _allowances[owner][spender];
    `}`
    function approve(address spender, uint amount) public returns (bool) `{`
        _approve(msg.sender, spender, amount);
        return true;
    `}`
    function _approve(address owner, address spender, uint amount) internal `{`
        require(owner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");

        _allowances[owner][spender] = amount;
        emit Approval(owner, spender, amount);
    `}`
    function mint(address account, uint amount) external `{`
        require(account != address(0), "ERC20: mint to the zero address");

        _totalSupply = _totalSupply.add(amount);
        _balances[account] = _balances[account].add(amount);
        emit Transfer(address(0), account, amount);
    `}`

    function _transfer(address _from ,address _to, uint256 _value) internal returns (bool) `{`
        require(_to != address(0));
        require(_value &lt;= _balances[msg.sender]);

        _balances[_from] = _balances[_from].sub(_value, "ERC20: transfer amount exceeds balance");
        _balances[_to] = _balances[_to].add(_value);
        emit Transfer(_from, _to, _value);
        return true;
    `}`
    function transfer(address to, uint value) public returns (bool) `{`
        _transfer(msg.sender, to, value);
        //return true;//无显式return,默认返回false
    `}`
    function transferFrom(address from, address to, uint value) public returns (bool) `{`
        _transfer(from, to, value);
        _approve(from, msg.sender, _allowances[from][msg.sender].sub(value, "ERC20: transfer amount exceeds allowance"));
        return true;
    `}`
`}`
```

Myrose模拟测试合约代码如下：

```
pragma solidity ^0.5.0;

import "IERC20.sol";
import "Address.sol";
import "SafeERC20.sol";
import "SafeMath.sol";

contract Test `{`
    using Address for address;
    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    uint256 internal _totalSupply;
    mapping(address =&gt; uint256) internal _balances;

    constructor() public `{`
        _totalSupply = 1 * 10 ** 18;
        _balances[msg.sender] = _totalSupply;
    `}`
    function totalSupply() external view returns (uint256) `{`
        return _totalSupply;
    `}`
    function balanceOf(address account) external view returns (uint256) `{`
        return _balances[account];
    `}`

    function withdraw(address yAddr,uint256 amount) public `{`
        _totalSupply = _totalSupply.sub(amount);
        _balances[msg.sender] = _balances[msg.sender].sub(amount);
        IERC20 y = IERC20(yAddr);
        y.safeTransfer(msg.sender, amount);
    `}`
`}`
```

Remix部署`USDT_Ethereum`、`USDT_Tron`、`Test`三个合约。

调用USDT_Ethereum和USDT_Tron的`mint`函数给Test合约地址增添一些代币。

然后调用Test合约的`withdraw`函数提现测试。

[![](https://p0.ssl.qhimg.com/t01200856d23a306c5f.png)](https://p0.ssl.qhimg.com/t01200856d23a306c5f.png)

可以看到`USDT_Ethereum`提现成功，`USDT_Tron`提现失败。

失败的回滚信息中，正是`safeTransfer`函数中对最后返回值的校验。

```
function safeTransfer(IERC20 token, address to, uint value) internal `{`
    callOptionalReturn(token, abi.encodeWithSelector(token.transfer.selector, to, value));
`}`

function callOptionalReturn(IERC20 token, bytes memory data) private `{`
    require(address(token).isContract(), "SafeERC20: call to non-contract");

    // solhint-disable-next-line avoid-low-level-calls
    (bool success, bytes memory returndata) = address(token).call(data);
    require(success, "SafeERC20: low-level call failed");

    if (returndata.length &gt; 0) `{` // Return data is optional
        // solhint-disable-next-line max-line-length
        require(abi.decode(returndata, (bool)), "SafeERC20: ERC20 operation did not succeed");//require校验返回的bool数值，false则回滚，提示操作失败
    `}`
`}`
```



## Missing Return Value Bug

上文的合约模拟实验揭示了以太坊与波场两个不同平台下USDT代币合约中transfer函数关于返回值处理差异性带来的安全风险，而关于”missing return value bug”这一个问题，早在2018年就有研究人员在Medium上公开讨论过，只不过是针对以太坊的，这里对以太坊中的”missing return value bug”问题做一个简单的介绍：

ERC20标准是以太坊平台上最常见的Token标准，ERC20被定义为一个接口，该接口指定在符合ERC20的智能合同中必须实现哪些功能和事件。目前，主要的接口如下所示：

```
interface ERC20Interface `{`

    function totalSupply() external constant returns (uint);
    function balanceOf(address tokenOwner) external constant returns (uint balance);
    function allowance(address tokenOwner, address spender) external constant returns (uint remaining);
    function transfer(address to, uint tokens) external returns (bool success);
    function approve(address spender, uint tokens) external returns (bool success);
    function transferFrom(address from, address to, uint tokens) external returns (bool success);

    event Transfer(address indexed from, address indexed to, uint tokens);
    event Approval(address indexed tokenOwner, address indexed spender, uint tokens);
`}`
```

在ERC20的开发过程中，有研究人员对于ERC20合约中的transfer函数的正确返回值进行了讨论，主要分为两个阵营：一方认为，如果transfer函数允许在调用合约中处理Failed error，那么应该在被调用合约中返回false值，另一方声称，在无法确保安全的情况下，ERC20应该revert交易，关于这个问题在当时被认为都是符合ERC20标准的，并未达成一致。

事实证明，很大比例的ERC20 Token在传递函数的返回值方面表现出了另一种特殊的方式，有些智能合约的Transfer函数不返回任何东西，对应的函数接口大致如下：

```
interface BadERC20Basic `{`
  function balanceOf(address who) external constant returns (uint);
  function transfer(address to, uint value) external;
  function allowance(address owner, address spender) external constant returns (uint);
  function transferFrom(address from, address to, uint value) external;
  function approve(address spender, uint value) external;

  event Approval(address indexed owner, address indexed spender, uint value);
  event Transfer(address indexed from, address indexed to, uint value);
`}`
```

那么符合ERC20标准的接口的合约试图与不符合ERC20的合约进行交互，会发生什么呢？下面我们通过一个合约示例来做解释说明：

```
interface Token `{`
  function transfer() returns (bool);
`}`

contract GoodToken is Token `{`
  function transfer() returns (bool) `{` return true; `}`
`}`

contract BadToken `{`
  function transfer() `{``}`
`}`

contract Wallet `{`
  function transfer(address token) `{`
    require(Token(token).transfer());
  `}`
`}`
```

在solidity中，函数选择器是从它的函数名和输入参数的类型中派生出来的：

```
selector = bytes4(sha3(“transfer()”))
```

函数的返回值不是函数选择器的一部分，因此，没有返回值的函数transfer()和函数transfer()返回(bool)具有相同的函数选择器，但它们仍然不同，由于缺少返回值，编译器不会接受transfer()函数作为令牌接口的实现，所以Goodtoken是Token接口的实现，而Badtoken不是。

当我们通过合约去外部调用BadToken时，Bad token会处理该transfer调用，并且不返回布尔返回值，之后调用合约会在内存中查找返回值，但是由于被调用的合约中的Transfer函数没有写返回值，所以它会将在这个内存位置找到的任何内容作为外部调用的返回值。

完全巧合的是，因为调用方期望返回值的内存槽与存储调用的函数选择器的内存槽重叠，这被EVM解释为返回值“真”。因此，完全是运气使然，EVM的表现就像程序员们希望它的表现一样。

自从去年10月拜占庭硬叉以来，EVM有了一个新的操作码，叫做`returndatasize`，这个操作码存储(顾名思义)外部调用返回数据的大小，这是一个非常有用的操作码，因为它允许在函数调用中返回动态大小的数组。

这个操作码在solidity 0.4.22更新中被采用，现在，代码在外部调用后检查返回值的大小，并在返回数据比预期的短的情况下revert事务，这比从某个内存插槽中读取数据安全得多，但是这种新的行为对于我们的BadToken来说是一个巨大的问题。

如上所述，最大的风险是用solc ≥ 0.4.22编译的智能合约(预期为ERC0接口)将无法与我们的Badtokens交互，这可能意味着发送到这样的合约的Token将永远停留在那里，即使该合约具有转移ERC 20 Token的功能。

类似问题的合约：

```
`{`'addr': '0xae616e72d3d89e847f74e8ace41ca68bbf56af79', 'name': 'GOOD', 'decimals': 6`}`
`{`'addr': '0x93e682107d1e9defb0b5ee701c71707a4b2e46bc', 'name': 'MCAP', 'decimals': 8`}`
`{`'addr': '0xb97048628db6b661d4c2aa833e95dbe1a905b280', 'name': 'PAY', 'decimals': 18`}`
`{`'addr': '0x4470bb87d77b963a013db939be332f927f2b992e', 'name': 'ADX', 'decimals': 4`}`
`{`'addr': '0xd26114cd6ee289accf82350c8d8487fedb8a0c07', 'name': 'OMG', 'decimals': 18`}`
`{`'addr': '0xb8c77482e45f1f44de1745f52c74426c631bdd52', 'name': 'BNB', 'decimals': 18`}`
`{`'addr': '0xf433089366899d83a9f26a773d59ec7ecf30355e', 'name': 'MTL', 'decimals': 8`}`
`{`'addr': '0xc63e7b1dece63a77ed7e4aeef5efb3b05c81438d', 'name': 'FUCKOLD', 'decimals': 4`}`
`{`'addr': '0xab16e0d25c06cb376259cc18c1de4aca57605589', 'name': 'FUCK', 'decimals': 4`}`
`{`'addr': '0xe3818504c1b32bf1557b16c238b2e01fd3149c17', 'name': 'PLR', 'decimals': 18`}`
`{`'addr': '0xe2e6d4be086c6938b53b22144855eef674281639', 'name': 'LNK', 'decimals': 18`}`
`{`'addr': '0x2bdc0d42996017fce214b21607a515da41a9e0c5', 'name': 'SKIN', 'decimals': 6`}`
`{`'addr': '0xea1f346faf023f974eb5adaf088bbcdf02d761f4', 'name': 'TIX', 'decimals': 18`}`
`{`'addr': '0x177d39ac676ed1c67a2b268ad7f1e58826e5b0af', 'name': 'CDT', 'decimals': 18`}`
```

有两种方法可以修复这个错误：

第一种：受影响的Token合约开放团队需要修改他们的合约，这可以通过重新部署Token合约或者更新合约来完成(如果有合约更新逻辑设计)。

第二种：重新包装Bad Transfer函数，对于这种包装有不同的建议，例如：

```
library ERC20SafeTransfer `{`
    function safeTransfer(address _tokenAddress, address _to, uint256 _value) internal returns (bool success) `{`
        // note: both of these could be replaced with manual mstore's to reduce cost if desired
        bytes memory msg = abi.encodeWithSignature("transfer(address,uint256)", _to, _value);
        uint msgSize = msg.length;

        assembly `{`
            // pre-set scratch space to all bits set
            mstore(0x00, 0xff)

            // note: this requires tangerine whistle compatible EVM
            if iszero(call(gas(), _tokenAddress, 0, add(msg, 0x20), msgSize, 0x00, 0x20)) `{` revert(0, 0) `}`

            switch mload(0x00)
            case 0xff `{`
                // token is not fully ERC20 compatible, didn't return anything, assume it was successful
                success := 1
            `}`
            case 0x01 `{`
                success := 1
            `}`
            case 0x00 `{`
                success := 0
            `}`
            default `{`
                // unexpected value, what could this be?
                revert(0, 0)
            `}`
        `}`
    `}`
`}`

interface ERC20 `{`
    function transfer(address _to, uint256 _value) returns (bool success);
`}`

contract TestERC20SafeTransfer `{`
    using ERC20SafeTransfer for ERC20;
    function ping(address _token, address _to, uint _amount) `{`
        require(ERC20(_token).safeTransfer(_to, _amount));
    `}`
`}`
```

另一方面，正在编写ERC 20合约的开发人员需要意识到这个错误，这样他们就可以预料到BadToken的意外行为并处理它们，这可以通过预期BadER 20接口并在调用后检查返回数据来确定我们调用的是Godtoken还是BadToken来实现：

```
pragma solidity ^0.4.24;

/*
 * WARNING: Proof of concept. Do not use in production. No warranty.
*/

interface BadERC20 `{`

  function transfer(address to, uint value) external;
`}`

contract BadERC20Aware `{`

    function safeTransfer(address token, address to , uint value) public returns (bool result) `{`
        BadERC20(token).transfer(to,value);

        assembly `{`
            switch returndatasize()   
                case 0 `{`                      // This is our BadToken
                    result := not(0)          // result is true
                `}`
                case 32 `{`                     // This is our GoodToken
                    returndatacopy(0, 0, 32) 
                    result := mload(0)        // result == returndata of external call
                `}`
                default `{`                     // This is not an ERC20 token
                    revert(0, 0) 
                `}`
        `}`
    require(result);                          // revert() if result is false
    `}`
`}`
```



## 事件总结

造成本次事件的主要原因还是在于波场USDT的transfer函数未使用TIP20规范的写法导致函数在执行时未返回对应的值，最终返回默认的false，从而导致在使用safeTransfer调用USDT的transfer时永远都只返回false，导致用户无法提现。

所以，在波场部署有关USDT的合约，需要注意额外针对USDT合约进行适配，上线前务必做好充足的审计与测试，尽可能减少意外事件的发生

知道创宇提供规避因合约安全问题导致的财产损失，为区块链应用提供专属安全解决方案。

## 参考链接

[1] Missing-Return-Value-Bug<br>[https://medium.com/coinmonks/missing-return-value-bug-at-least-130-tokens-affected-d67bf08521ca](https://medium.com/coinmonks/missing-return-value-bug-at-least-130-tokens-affected-d67bf08521ca)
