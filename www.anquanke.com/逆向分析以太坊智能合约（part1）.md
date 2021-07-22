> 原文链接: https://www.anquanke.com//post/id/101979 


# 逆向分析以太坊智能合约（part1）


                                阅读量   
                                **171336**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Brandon Arvanaghi，文章来源：arvanaghi.com
                                <br>原文地址：[https://arvanaghi.com/blog/reversing-ethereum-smart-contracts/](https://arvanaghi.com/blog/reversing-ethereum-smart-contracts/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0142b07a79c7dc90a8.png)](https://p3.ssl.qhimg.com/t0142b07a79c7dc90a8.png)



**逆向分析以太坊智能合约（part2）  传送门：[https://www.anquanke.com/post/id/106984](https://www.anquanke.com/post/id/106984)**



## 一、前言

在本文中，我会向大家介绍以太坊虚拟机（Ethereum Virtual Machine，EVM）的工作原理，以及如何对智能合约（smart contract）进行逆向分析。

为了反汇编智能合约，我使用了Trail of Bits开发的适用于[Binary Ninja](https://binary.ninja/)的[Ethersplay](https://github.com/trailofbits/ethersplay)插件。



## 二、以太坊虚拟机

以太坊虚拟机（EVM）是一种**基于栈**的、**准图灵完备**（quasi-Turing complete）的虚拟机。

1）**基于栈**：EVM并不依赖寄存器，任何操作都会在栈中完成。操作数、运算符以及函数调用都置于栈中，并且EVM知道如何处理数据、执行智能合约。

以太坊使用Postfix Notation（后缀表示法）来实现基于栈的运行机制。简而言之，操作符最后压入栈，可以作用于先前压入栈的数据。

举个例子：来看一下`2 + 2`操作，在脑海中，我们知道中间的运算符（`+`）表示我们想执行2加2这个操作。将`+`放在两个操作数之间是一种办法，我们也可以将它放在两个操作数后面，即`2 2 +`，这就是后缀表示法。

2）**准图灵完备**：如果一切可计算的问题都能计算，那么这样的编程语言或者代码执行引擎就可以称为“图灵完备（Turing complete）”。这个概念并不在意解决问题的时间长短，只要理论上该问题能被解决即可。比特币脚本语言不能称为图灵完备语言，因为该语言的应用场景非常有限。

在EVM中，我们可以解决所有问题。但我们还是将其成为“准图灵完备”，这主要是因为成本限制问题。`gas`是EVM中的一个可计算单位，可以用来衡量操作所需的成本。当某人在区块链上发起交易时，交易代码以及待执行的任何后续代码都需要在矿工的主机上执行。由于代码需要在矿工的内存中执行，这个过程会消耗矿工主机的成本，如电力成本、内存以及CPU计算成本等。

为了激励矿工来保证交易顺利进行，发起交易的那个人需要声明`gas price`，或者他们愿意为每个计算单元支付的价格。将这个因素考虑在内后，对于非常复杂的问题，所需的gas量将变得非常庞大，此时由于我们需要为gas定价，因此在以太坊中，从经济角度来考虑的话复杂的交易并不划算。



## 三、Bytecode以及Runtime Bytecode

在编译合约时，我们可以得到**contract bytecode**（合约字节码）或者**runtime bytecode**（运行时字节码）。

**contract bytecode**是最终存储在区块链中的字节码，也是将字节码存放在区块链、初始化智能合约（运行构造函数）时所需的字节码。

**runtime bytecode**只对应于存储在区块链中的字节码，与合约初始化和存放过程无关。

让我们以`Greeter.sol`合约为例来分析两者的不同点。

```
contract mortal `{`
    /* Define variable owner of the type address */
    address owner;

    /* This function is executed at initialization and sets the owner of the contract */
    function mortal() `{` owner = msg.sender; `}`

    /* Function to recover the funds on the contract */
    function kill() `{` if (msg.sender == owner) selfdestruct(owner); `}`
`}`

contract greeter is mortal `{`
    /* Define variable greeting of the type string */
    string greeting;

    /* This runs when the contract is executed */
    function greeter(string _greeting) public `{`
        greeting = _greeting;
    `}`

    /* Main function */
    function greet() constant returns (string) `{`
        return greeting;
    `}`
`}`
```

使用`solc --bin Greeter.sol`命令来编译合约、获取合约字节码时，我们可以得到如下结果：

```
6060604052341561000f57600080fd5b6040516103a93803806103a983398101604052808051820191905050336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055508060019080519060200190610081929190610088565b505061012d565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106100c957805160ff19168380011785556100f7565b828001600101855582156100f7579182015b828111156100f65782518255916020019190600101906100db565b5b5090506101049190610108565b5090565b61012a91905b8082111561012657600081600090555060010161010e565b5090565b90565b61026d8061013c6000396000f30060606040526004361061004c576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806341c0e1b514610051578063cfae321714610066575b600080fd5b341561005c57600080fd5b6100646100f4565b005b341561007157600080fd5b610079610185565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156100b957808201518184015260208101905061009e565b50505050905090810190601f1680156100e65780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161415610183576000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16ff5b565b61018d61022d565b60018054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102235780601f106101f857610100808354040283529160200191610223565b820191906000526020600020905b81548152906001019060200180831161020657829003601f168201915b5050505050905090565b6020604051908101604052806000815250905600a165627a7a723058204138c228602c9c0426658c0d46685e1d9c157ff1f92cb6e28acb9124230493210029
```

如果使用`solc --bin-runtime Greeter.sol`命令来编译时，我们可以得到如下结果：

```
60606040526004361061004c576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806341c0e1b514610051578063cfae321714610066575b600080fd5b341561005c57600080fd5b6100646100f4565b005b341561007157600080fd5b610079610185565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156100b957808201518184015260208101905061009e565b50505050905090810190601f1680156100e65780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161415610183576000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16ff5b565b61018d61022d565b60018054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102235780601f106101f857610100808354040283529160200191610223565b820191906000526020600020905b81548152906001019060200180831161020657829003601f168201915b5050505050905090565b6020604051908101604052806000815250905600a165627a7a723058204138c228602c9c0426658c0d46685e1d9c157ff1f92cb6e28acb9124230493210029
```

如上所示，我们可知runtime bytecode是contract bytecode的一个子集。

[![](https://p0.ssl.qhimg.com/t01f074f413654ab8ee.png)](https://p0.ssl.qhimg.com/t01f074f413654ab8ee.png)



## 四、逆向分析

在本文中，我们使用Trail of Bits为[Binary Ninja](https://binary.ninja/)开发的[Ethersplay](https://github.com/trailofbits/ethersplay)插件来反汇编以太坊字节码。

我们的操作对象是[Ethereum.org](https://ethereum.org/)提供的`Greeter.sol`合约。

首先，我们可以参考[教程](https://github.com/trailofbits/ethersplay)，将Ethersplay插件加入Binary Ninja中。这里提醒一下，我们只逆向runtime bytecode，因为这个过程足以告诉我们合约具体做了哪些工作。

### <a class="reference-link" name="%E5%B7%A5%E5%85%B7%E6%A6%82%E8%A7%88"></a>工具概览

[![](https://p0.ssl.qhimg.com/t01e65f40298787e981.png)](https://p0.ssl.qhimg.com/t01e65f40298787e981.png)

Ethersplay插件可以识别runtime bytecode中的所有函数，从逻辑上进行划分。对于这个合约，Ethersplay发现了两个函数：`kill()` 以及`greet()`。后面我们会介绍如何提取这些函数。

### <a class="reference-link" name="%E7%AC%AC%E4%B8%80%E6%9D%A1%E6%8C%87%E4%BB%A4"></a>第一条指令

当我们向智能合约发起交易时，首先碰到的是合约的dispatcher（调度器）。Dispatcher会处理交易数据，确定我们需要交互的具体函数。

[![](https://p5.ssl.qhimg.com/t01bc108658acb9c3fb.png)](https://p5.ssl.qhimg.com/t01bc108658acb9c3fb.png)

我们在dispatcher中看到的第一条指令为：

```
PUSH1 0x60 // argument 2 of mstore: the value to store in memory
PUSH1 0x40 // argument 1 of mstore: where to store that value in memory
MSTORE // mstore(0x40, 0x60)
PUSH1 0x4
CALLDATASIZE
LT
PUSH2 0x4c
JUMPI
```

`PUSH`指令有16个不同的版本（`PUSH1`… `PUSH16`）。EVM通过不同编号来了解我们往栈上压入了多少字节。

前两条指令（`PUSH1 0x60`以及`PUSH1 0x40`）分别代表将`0x60`以及 `0x40` 压入栈。这些指令执行完毕后，运行时栈的布局如下：

```
1: 0x40
0: 0x60
```

根据[Solidity官方文档](https://solidity.readthedocs.io/en/v0.4.21/assembly.html)，`MSTORE`的定义如下：

|指令|结果
|------
|mstore(p, v)|mem[p..(p+32)) := v

EVM会从栈顶到栈底来读取函数参数，也就是说会执行`mstore(0x40, 0x60)`，这条指令与`mem[0x40...0x40+32] := 0x60`作用相同。

`mstore`会从栈中取出两个元素，因此栈现在处于清空状态。接下来的指令为：

```
PUSH1 0x4
CALLDATASIZE
LT
PUSH 0x4c
JUMPI
```

`PUSH1 0x4`执行后，栈中只有一个元素：

```
0: 0x4
```

`CALLDATASIZE`函数会将**calldata**（相当于`msg.data`）的大小压入栈中。我们可以往任何智能合约发送任意数据，`CALLDATASIZE`会检查数据的大小。

调用`CALLDATASIZE`后，栈的布局如下：

```
1: (however long the msg.data or calldata is)
0: 0x4
```

下一条指令为`LT`（即“less than”），指令功能如下：

|指令|结果
|------
|mstore(p, v)|mem[p..(p+32)) := v
|lt(x, y)|如果x &lt; y则为1，否则为0

如果第一个参数小于第二个参数，则`lt`会将1压入栈，否则就压入0。在我们的例子中，根据此时的栈布局，这条指令为`lt((however long the msg.data or calldata is), 0x4)` （判断msg.data或calldata的大小是否小于0x4字节）。

为什么EVM需要检查我们提供的calldata大小是否至少为4字节？这里涉及到函数的识别过程。

EVM会通过函数`keccak256`哈希的前4个字节来识别函数。也就是说，函数原型（函数名以及所需参数）需要交给`keccak256`哈希函数处理。在这个合约中，我们可以得到如下结果：

```
keccak256("greet()") = cfae3217...
keccak256("kill()") = 41c0e1b5...
```

因此，`greet()`的函数标识符为`cfae3217`，`kill()`的函数标识符为`41c0e1b5`。Dispatcher会检查我们发往合约的`calldata`（或者消息数据）大小至少为4字节，以确保我们的确想跟某个函数交互。

函数标识符大小**始终**为4字节，因此如果我们发往智能合约的数据小于4字节，那么我们无法与任何函数交互。

事实上，我们可以在汇编代码中看到智能合约如何拒绝不符合规定的行为。如果`calldatasize`小于4字节，那么bytecode会立即跳到代码尾部，结束合约执行过程。

[![](https://p0.ssl.qhimg.com/t01b8cf87fea31b51b9.png)](https://p0.ssl.qhimg.com/t01b8cf87fea31b51b9.png)

来具体看一下判断过程。

如果`lt((however long the msg.data or calldata is), 0x4)` 等于`1`（为真，即calldata小于4字节），那么从栈中取出2个元素后，`lt`会往栈中压入1。

```
0: 1
```

接下来的指令为`PUSH 0x4c` 以及`JUMPI`。`PUSH 0x4c`指令执行后，栈的布局为：

```
1: 0x4c
0: 1
```

`JUMPI`代表的是“jump if”（条件满足则跳转），如果条件满足，则跳转到特定的标签或者位置。

|指令|结果
|------
|mstore(p, v)|mem[p..(p+32)) := v
|lt(x, y)|如果x &lt; y则为1，否则为0
|jumpi(label, cond)|如果cond非零则跳转至label

在这个例子中，`label`为代码中的`0x4c`偏移地址，并且`cond`为1，因此程序会跳转到`0x4c`偏移处。

### <a class="reference-link" name="%E5%87%BD%E6%95%B0%E8%B0%83%E5%BA%A6"></a>函数调度

来看一下如何从`calldata`中提取所需的函数。上一条`JUMPI`指令执行完毕后，栈处于清空状态。

[![](https://p1.ssl.qhimg.com/t019704b4e34189ca6d.png)](https://p1.ssl.qhimg.com/t019704b4e34189ca6d.png)

第二个代码块中的命令如下：

```
PUSH1 0x0
CALLDATALOAD
PUSH29 0x100000000....
SWAP1
DIV
PUSH4 0xffffffff
AND
DUP1
PUSH4 0x41c0e1b5
EQ
PUSH2 0x51
JUMPI
```

`PUSH1 0x0`会将0压入栈顶。

```
0: 0
```

`CALLDATALOAD`指令接受一个参数，该参数可以作为发往智能合约的calldata数据的索引，然后从该索引处再读取32个字节，指令说明如下：

|指令|结果
|------
|mstore(p, v)|mem[p..(p+32)) := v
|lt(x, y)|如果x &lt; y则为1，否则为0
|jumpi(label, cond)|如果cond非零则跳转至label
|calldataload(p)|从calldata的位置p处读取数据（32字节）

`CALLDATALOAD`会将读取到的32字节压入栈顶。由于该指令收到的索引值为0（来自于`PUSH1 0x0`命令），因此`CALLDATALOAD`会读取calldata中从0字节处开始的32个字节，然后将其压入栈顶（先弹出栈中的`0x0`）。新的栈布局为：

```
0: 32 bytes of calldata starting at byte 0
```

下一条指令为`PUSH29 0x100000000....`。

```
1: 0x100000000....
0: 32 bytes of calldata starting at byte 0
```

`SWAPi`指令会将栈顶元素与栈中第`i`个元素进行交换。在这个例子中，该指令为`SWAP1`，因此指令会将栈顶元素与随后的第一个元素交换。

|指令|结果
|------
|mstore(p, v)|mem[p..(p+32)) := v
|lt(x, y)|如果x &lt; y则为1，否则为0
|jumpi(label, cond)|如果cond非零则跳转至label
|calldataload(p)|从calldata的位置p处读取数据（32字节）
|swap1 … swap16|交换栈顶元素与随后的第i个元素

```
1: 32 bytes of calldata starting at byte 0
0: PUSH29 0x100000000....
```

下一跳指令为`DIV`，即`div(x, y)`也就是x/y。在这个例子中，x为`32 bytes of calldata starting at byte 0`，y为`0x100000000....`。

`0x100000000....`的大小为29个字节，最开头为1，后面全部都为0。先前我们从calldata中读取了32个字节，将32字节的calldata除以`10000...`，结果为calldataload从索引0开始的前4个字节。这4个字节其实就是函数标识符。

如果大家还不明白，可以类比一下10进制的除法，`123456000 / 100 = 123456`，在16进制中运算过程与之类似。将32字节的某个值除以29字节的某个值，结果只保留前4个字节。

`DIV`运算的结果也会压入栈中。

```
0: function identifier from calldata
```

接下来的指令为`PUSH4 0xffffffff`以及`AND`，这个例子中，对应的是将`0xffffffff`与calldata发过来的函数标识符进行`AND`操作。这样就把能栈中函数标识符的后28个字节清零。

随后是一条`DUP1`指令，可以复制栈中的第一个元素（这里对应的是函数标识符），然后将其压入栈顶。

```
1: function identifier from calldata
0: function identifier from calldata
```

接下来是`PUSH4 0x41c0e1b5`指令，这是`kill()`的函数标识符。我们将该标识符压入栈，目的是想将其与calldata的函数标识符进行对比。

```
2: 0x41c0e1b5
1: function identifier from calldata
0: function identifier from calldata
```

下一条指令为`EQ`（即`eq(x,y)`），该指令会将x以及y弹出栈，如果两者相等则压入1，否则压入0。这个过程正是dispatcher的“调度”过程：将calldata函数标识符与智能合约中所有的函数标识符进行对比。

```
1: (1 if calldata functio identifier matched kill() function identifier, 0 otherwise)
0: function identifier from calldata
```

执行完`PUSH2 0x51`后，栈的布局如下：

```
2: 0x51
1: (1 if calldata functio identifier matched kill() function identifier, 0 otherwise)
0: function identifier from calldata
```

之所以压入`0x51`，是希望条件满足时，可以通过`JUMPI`指令跳转到这个偏移处。换句话说，如果calldata发过来的函数标识符与`kill()`匹配，那么执行流程就会跳转到代码中的`0x51`偏移位置（即`kill()`函数所在位置）。

`JUMPI`执行之后，我们要么跳转到`0x51`偏移位置，要么继续执行当前流程。

[![](https://p3.ssl.qhimg.com/t0192cbcb9dd7ea1fd2.png)](https://p3.ssl.qhimg.com/t0192cbcb9dd7ea1fd2.png)

现在栈中只包含一个元素：

```
0: function identifier from calldata
```

细心的读者会注意到，如果我们没有跳转到`kill()`函数，那么dispatcher依然会采用相同逻辑，将calldata函数标识符与`greet()`函数标识符进行对比。Dispatcher会检查智能合约中的每个函数，如果不能找到匹配的函数，则会将我们引导至程序退出代码。



## 五、总结

以上是对以太坊虚拟机工作原理的简单介绍，大家如果想了解以太坊或者区块链安全方面内容，欢迎关注我的[推特](https://twitter.com/arvanaghi)。
