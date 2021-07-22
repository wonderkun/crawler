> 原文链接: https://www.anquanke.com//post/id/214757 


# 以太坊安全之 EVM 与短地址攻击


                                阅读量   
                                **204029**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t0178643240f69acf60.png)](https://p5.ssl.qhimg.com/t0178643240f69acf60.png)



**作者：昏鸦@知道创宇404区块链安全研究团队 **

## 前言

以太坊（Ethereum）是一个开源的有智能合约功能的公共区块链平台，通过其专用加密货币以太币（ETH）提供去中心化的以太坊虚拟机（EVM）来处理点对点合约。EVM（Ethereum Virtual Machine），以太坊虚拟机的简称，是以太坊的核心之一。智能合约的创建和执行都由EVM来完成，简单来说，EVM是一个状态执行的机器，输入是solidity编译后的二进制指令和节点的状态数据，输出是节点状态的改变。

以太坊短地址攻击，最早由Golem团队于2017年4月提出，是由于底层EVM的设计缺陷导致的漏洞。ERC20代币标准定义的转账函数如下：

`function transfer(address to, uint256 value) public returns (bool success)`

如果传入的`to`是末端缺省的短地址，EVM会将后面字节补足地址，而最后的`value`值不足则用0填充，导致实际转出的代币数值倍增。

本文从以太坊源码的角度分析EVM底层是如何处理执行智能合约字节码的，并简要分析短地址攻击的原理。



## EVM源码分析

### evm.go

EVM的源码位于`go-ethereum/core/vm/`目录下，在`evm.go`中定义了EVM结构体，并实现了`EVM.Call`、`EVM.CallCode`、`EVM.DelegateCall`、`EVM.StaticCall`四种方法来调用智能合约，`EVM.Call`实现了基本的合约调用的功能，后面三种方法与`EVM.Call`略有区别，但最终都调用`run`函数来解析执行智能合约



### EVM.Call

```
// Call executes the contract associated with the addr with the given input as
// parameters. It also handles any necessary value transfer required and takes
// the necessary steps to create accounts and reverses the state in case of an
// execution error or failed value transfer.
//hunya// 基本的合约调用
func (evm *EVM) Call(caller ContractRef, addr common.Address, input []byte, gas uint64, value *big.Int) (ret []byte, leftOverGas uint64, err error) `{`
    if evm.vmConfig.NoRecursion &amp;&amp; evm.depth &gt; 0 `{`
        return nil, gas, nil
    `}`

    // Fail if we're trying to execute above the call depth limit
    if evm.depth &gt; int(params.CallCreateDepth) `{`
        return nil, gas, ErrDepth
    `}`
    // Fail if we're trying to transfer more than the available balance
    if !evm.Context.CanTransfer(evm.StateDB, caller.Address(), value) `{`
        return nil, gas, ErrInsufficientBalance
    `}`

    var (
        to       = AccountRef(addr)
        snapshot = evm.StateDB.Snapshot()
    )
    if !evm.StateDB.Exist(addr) `{`
        precompiles := PrecompiledContractsHomestead
        if evm.chainRules.IsByzantium `{`
            precompiles = PrecompiledContractsByzantium
        `}`
        if evm.chainRules.IsIstanbul `{`
            precompiles = PrecompiledContractsIstanbul
        `}`
        if precompiles[addr] == nil &amp;&amp; evm.chainRules.IsEIP158 &amp;&amp; value.Sign() == 0 `{`
            // Calling a non existing account, don't do anything, but ping the tracer
            if evm.vmConfig.Debug &amp;&amp; evm.depth == 0 `{`
                evm.vmConfig.Tracer.CaptureStart(caller.Address(), addr, false, input, gas, value)
                evm.vmConfig.Tracer.CaptureEnd(ret, 0, 0, nil)
            `}`
            return nil, gas, nil
        `}`
        evm.StateDB.CreateAccount(addr)
    `}`
    evm.Transfer(evm.StateDB, caller.Address(), to.Address(), value)
    // Initialise a new contract and set the code that is to be used by the EVM.
    // The contract is a scoped environment for this execution context only.
    contract := NewContract(caller, to, value, gas)
    contract.SetCallCode(&amp;addr, evm.StateDB.GetCodeHash(addr), evm.StateDB.GetCode(addr))

    // Even if the account has no code, we need to continue because it might be a precompile
    start := time.Now()

    // Capture the tracer start/end events in debug mode
    // debug模式会捕获tracer的start/end事件
    if evm.vmConfig.Debug &amp;&amp; evm.depth == 0 `{`
        evm.vmConfig.Tracer.CaptureStart(caller.Address(), addr, false, input, gas, value)

        defer func() `{` // Lazy evaluation of the parameters
            evm.vmConfig.Tracer.CaptureEnd(ret, gas-contract.Gas, time.Since(start), err)
        `}`()
    `}`
    ret, err = run(evm, contract, input, false)//hunya// 调用run函数执行合约

    // When an error was returned by the EVM or when setting the creation code
    // above we revert to the snapshot and consume any gas remaining. Additionally
    // when we're in homestead this also counts for code storage gas errors.
    if err != nil `{`
        evm.StateDB.RevertToSnapshot(snapshot)
        if err != errExecutionReverted `{`
            contract.UseGas(contract.Gas)
        `}`
    `}`
    return ret, contract.Gas, err
`}`
```

###### 

### EVM.CallCode

```
// CallCode executes the contract associated with the addr with the given input
// as parameters. It also handles any necessary value transfer required and takes
// the necessary steps to create accounts and reverses the state in case of an
// execution error or failed value transfer.
//
// CallCode differs from Call in the sense that it executes the given address'
// code with the caller as context.
//hunya// 类似solidity中的call函数，调用外部合约，执行上下文在被调用合约中
func (evm *EVM) CallCode(caller ContractRef, addr common.Address, input []byte, gas uint64, value *big.Int) (ret []byte, leftOverGas uint64, err error) `{`
    if evm.vmConfig.NoRecursion &amp;&amp; evm.depth &gt; 0 `{`
        return nil, gas, nil
    `}`

    // Fail if we're trying to execute above the call depth limit
    if evm.depth &gt; int(params.CallCreateDepth) `{`
        return nil, gas, ErrDepth
    `}`
    // Fail if we're trying to transfer more than the available balance
    if !evm.CanTransfer(evm.StateDB, caller.Address(), value) `{`
        return nil, gas, ErrInsufficientBalance
    `}`

    var (
        snapshot = evm.StateDB.Snapshot()
        to       = AccountRef(caller.Address())
    )
    // Initialise a new contract and set the code that is to be used by the EVM.
    // The contract is a scoped environment for this execution context only.
    contract := NewContract(caller, to, value, gas)
    contract.SetCallCode(&amp;addr, evm.StateDB.GetCodeHash(addr), evm.StateDB.GetCode(addr))

    ret, err = run(evm, contract, input, false)//hunya// 调用run函数执行合约
    if err != nil `{`
        evm.StateDB.RevertToSnapshot(snapshot)
        if err != errExecutionReverted `{`
            contract.UseGas(contract.Gas)
        `}`
    `}`
    return ret, contract.Gas, err
`}`
```



### EVM.DelegateCall

```
// DelegateCall executes the contract associated with the addr with the given input
// as parameters. It reverses the state in case of an execution error.
//
// DelegateCall differs from CallCode in the sense that it executes the given address'
// code with the caller as context and the caller is set to the caller of the caller.
//hunya// 类似solidity中的delegatecall函数，调用外部合约，执行上下文在调用合约中
func (evm *EVM) DelegateCall(caller ContractRef, addr common.Address, input []byte, gas uint64) (ret []byte, leftOverGas uint64, err error) `{`
    if evm.vmConfig.NoRecursion &amp;&amp; evm.depth &gt; 0 `{`
        return nil, gas, nil
    `}`
    // Fail if we're trying to execute above the call depth limit
    if evm.depth &gt; int(params.CallCreateDepth) `{`
        return nil, gas, ErrDepth
    `}`

    var (
        snapshot = evm.StateDB.Snapshot()
        to       = AccountRef(caller.Address())
    )

    // Initialise a new contract and make initialise the delegate values
    contract := NewContract(caller, to, nil, gas).AsDelegate()
    contract.SetCallCode(&amp;addr, evm.StateDB.GetCodeHash(addr), evm.StateDB.GetCode(addr))

    ret, err = run(evm, contract, input, false)//hunya// 调用run函数执行合约
    if err != nil `{`
        evm.StateDB.RevertToSnapshot(snapshot)
        if err != errExecutionReverted `{`
            contract.UseGas(contract.Gas)
        `}`
    `}`
    return ret, contract.Gas, err
`}`
```



### EVM.StaticCall

```
// StaticCall executes the contract associated with the addr with the given input
// as parameters while disallowing any modifications to the state during the call.
// Opcodes that attempt to perform such modifications will result in exceptions
// instead of performing the modifications.
//hunya// 与EVM.Call类似，但不允许执行会修改永久存储的数据的指令
func (evm *EVM) StaticCall(caller ContractRef, addr common.Address, input []byte, gas uint64) (ret []byte, leftOverGas uint64, err error) `{`
    if evm.vmConfig.NoRecursion &amp;&amp; evm.depth &gt; 0 `{`
        return nil, gas, nil
    `}`
    // Fail if we're trying to execute above the call depth limit
    if evm.depth &gt; int(params.CallCreateDepth) `{`
        return nil, gas, ErrDepth
    `}`

    var (
        to       = AccountRef(addr)
        snapshot = evm.StateDB.Snapshot()
    )
    // Initialise a new contract and set the code that is to be used by the EVM.
    // The contract is a scoped environment for this execution context only.
    contract := NewContract(caller, to, new(big.Int), gas)
    contract.SetCallCode(&amp;addr, evm.StateDB.GetCodeHash(addr), evm.StateDB.GetCode(addr))

    // We do an AddBalance of zero here, just in order to trigger a touch.
    // This doesn't matter on Mainnet, where all empties are gone at the time of Byzantium,
    // but is the correct thing to do and matters on other networks, in tests, and potential
    // future scenarios
    evm.StateDB.AddBalance(addr, bigZero)

    // When an error was returned by the EVM or when setting the creation code
    // above we revert to the snapshot and consume any gas remaining. Additionally
    // when we're in Homestead this also counts for code storage gas errors.
    ret, err = run(evm, contract, input, true)//hunya// 调用run函数执行合约
    if err != nil `{`
        evm.StateDB.RevertToSnapshot(snapshot)
        if err != errExecutionReverted `{`
            contract.UseGas(contract.Gas)
        `}`
    `}`
    return ret, contract.Gas, err
`}`
```

`run`函数前半段是判断是否是以太坊内置预编译的特殊合约，有单独的运行方式

后半段则是对于一般的合约调用解释器`interpreter`去执行调用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/08/18/1597731232000-func-run.png-w331s)

### interpreter.go

解释器相关代码在`interpreter.go`中，`interpreter`是一个接口，目前仅有`EVMInterpreter`这一个具体实现

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/08/18/1597731232000-func-interpreter.png-w331s)

合约经由`EVM.Call`调用`Interpreter.Run`来到`EVMInpreter.Run`

`EVMInterpreter`的`Run`方法代码较长，其中处理执行合约字节码的主循环如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/08/18/1597731232000-func-interpreter-run-loop.png-w331s)

大部分代码主要是检查准备运行环境，执行合约字节码的核心代码主要是以下3行

```
op = contract.GetOp(pc)
operation := in.cfg.JumpTable[op]
......
res, err = operation.execute(&amp;pc, in, contract, mem, stack)
......
```

`interpreter`的主要工作实际上只是通过`JumpTable`查找指令，起到一个翻译解析的作用

最终的执行是通过调用`operation`对象的`execute`方法



### jump_table.go

`operation`的定义位于`jump_table.go`中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/08/18/1597731232000-func-operation.png-w331s)

`jump_table.go`中还定义了`JumpTable`和多种不同的指令集

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/08/18/1597731232000-func-jumptable.png-w331s)

在基本指令集中有三个处理`input`的指令，分别是`CALLDATALOAD`、`CALLDATASIZE`和`CALLDATACOPY`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/08/18/1597731233000-func-jumptable-calldata.png-w331s)

`jump_table.go`中的代码同样只是起到解析的功能，提供了指令的查找，定义了每个指令具体的执行函数



### instructions.go

`instructions.go`中是所有指令的具体实现，上述三个函数的具体实现如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/08/18/1597731233000-func-opCallData.png-w331s)

这三个函数的作用分别是从`input`加载参数入栈、获取`input`大小、复制`input`中的参数到内存

我们重点关注`opCallDataLoad`函数是如何处理`input`中的参数入栈的

`opCallDataLoad`函数调用`getDataBig`函数，传入`contract.Input`、`stack.pop()`和`big32`，将结果转为`big.Int`入栈

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/08/18/1597731233000-func-getdatabig.png-w331s)

`getDataBig`函数以`stack.pop()`栈顶元素作为起始索引，截取`input`中`big32`大小的数据，然后传入`common.RightPadBytes`处理并返回

其中涉及到的另外两个函数`math.BigMin`和`common.RightPadBytes`如下：

```
//file: go-thereum/common/math/big.go
func BigMin(x, y *big.Int) *big.Int `{`
    if x.Cmp(y) &gt; 0 `{`
        return y
    `}`
    return x
`}`
//file: go-ethereum/common/bytes.go
func RightPadBytes(slice []byte, l int) []byte `{`
    if l &lt;= len(slice) `{`
        return slice
    `}`
    //右填充0x00至l位
    padded := make([]byte, l)
    copy(padded, slice)

    return padded
`}`
```

分析到这里，基本上已经能很明显看到问题所在了

`RightPadBytes`函数会将传入的字节切片右填充至`l`位长度，而`l`是被传入的`big32`，即32位长度

所以在短地址攻击中，调用的`transfer(address to, uint256 value)`函数，如果`to`是低位缺省的地址，由于EVM在处理时是固定截取32位长度的，所以会将`value`数值高位补的0算进`to`的末端，而在截取`value`时由于位数不够32位，则右填充`0x00`至32位，最终导致转账的`value`指数级增大。



## 测试与复现

编写一个简单的合约来测试

```
pragma solidity ^0.5.0;

contract Test `{`
    uint256 internal _totalSupply;

    mapping(address =&gt; uint256) internal _balances;

    event Transfer(address indexed from, address indexed to, uint256 value);

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

    function transfer(address to,uint256 value) public returns (bool) `{`
        require(to != address(0));
        require(_balances[msg.sender] &gt;= value);
        require(_balances[to] + value &gt;= _balances[to]);

        _balances[msg.sender] -= value;
        _balances[to] += value;
        emit Transfer(msg.sender, to, value);
    `}`
`}`
```

remix部署，调用`transfer`发起正常的转账

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/08/18/1597731233000-remix-transfer.png-w331s)

`input`为`0xa9059cbb00000000000000000000000071430fd8c82cc7b991a8455fc6ea5b37a06d393f0000000000000000000000000000000000000000000000000000000000000001`

直接尝试短地址攻击，删去转账地址的后两位，会发现并不能通过，remix会直接报错

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/08/18/1597731233000-remix-error.png-w331s)

这是因为`web3.js`做了校验，`web3.js`是用户与以太坊节点交互的媒介



### 源码复现

通过源码函数复现如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/08/18/1597731233000-shortAddrAttack-demo.png-w331s)

### 实际复现

至于如何完成实际场景的攻击，可以参考文末的链接[1]，利用`web3.eth.sendSignedTransaction`绕过限制

实际上，`web3.js`做的校验仅限于显式传入转账地址的函数，如`web3.eth.sendTransaction`这种，像`web3.eth.sendSignedTransaction`、`web3.eth.sendRawTransaction`这种传入的参数是序列化后的数据的就校验不了，是可以完成短地址攻击的，感兴趣的可以自己尝试，这里就不多写了

PS：文中分析的`go-ethereum`源码版本是`commit-fdff182`，源码与最新版有些出入，但最新版的也未修复这种缺陷（可能官方不认为这是缺陷?），分析思路依然可以沿用



## 思考

以太坊底层EVM并没有修复短地址攻击的这么一个缺陷，而是直接在`web3.js`里对地址做的校验，目前各种合约或多或少也做了校验，所以虽然EVM底层可以复现，但实际场景中问题应该不大，但如果是开放RPC的节点可能还是会存在这种风险

另外还有一个点，按底层EVM的这种机制，易受攻击的应该不仅仅是`transfer(address to, uint256 value)`这个点，只是因为这个函数是ERC20代币标准，而且参数的设计恰好能导致涉及金额的短地址攻击，并且特殊的地址易构造，所以这个函数常作为短地址攻击的典型。在其他的一些非代币合约，如竞猜、游戏类的合约中，一些非转账类的事务处理函数中，如果不对类似地址这种的参数做长度校验，可能也存在类似短地址攻击的风险，也或者并不局限于地址，可能还有其他的利用方式还没挖掘出来。



## 参考

[1] 以太坊短地址攻击详解

[https://www.anquanke.com/post/id/159453](https://www.anquanke.com/post/id/159453)[/https://www.anquanke.com/post/id/159453](//www.anquanke.com/post/id/159453)

[2] 以太坊源码解析：evm

[https://www.jianshu.com/p/f319c78e9714](https://www.jianshu.com/p/f319c78e9714)[/https://www.jianshu.com/p/f319c78e9714](//www.jianshu.com/p/f319c78e9714)
