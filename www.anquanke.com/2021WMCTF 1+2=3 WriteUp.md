> 原文链接: https://www.anquanke.com//post/id/251985 


# 2021WMCTF 1+2=3 WriteUp


                                阅读量   
                                **15224**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01deaa2f252ff9e789.jpg)](https://p0.ssl.qhimg.com/t01deaa2f252ff9e789.jpg)



## 题目描述

题目在经过 `pow` 验证后交互的内容如下：

```
We design a pretty easy contract game. Enjoy it!
1. Create a game account
2. Deploy a game contract
3. Request for flag
4. Get source code
Option 1, get an account which will be used to deploy the contract;
Before option 2, please transfer some eth to this account (for gas);
Option 2, the robot will use the account to deploy the contract for the challenge;
Option 3, use this option to obtain the flag when isSolved() function returns true;
Option 4, use this option to get source code.
You can finish this challenge in a lot of connections.

You can get Ether from faucet &lt;http://ip:10001&gt;

[-]input your choice:
```

我们可以通过选项 `4` 获得题目的代码：

```
pragma solidity 0.8.0;

contract Dumper `{`
    constructor(bytes memory code) `{`
        assembly `{`
            return(add(code, 0x20), mload(code))
        `}`
    `}`
`}`

interface Storage `{`
    function getNumber() external view returns (uint256);
`}`

contract Puzzle `{`
    Storage public Storage1;
    Storage public Storage2;
    Storage public Storage3;

    bool public solved;

    function check(bytes memory code) private returns (bool) `{`
        uint256 i = 0;
        while (i &lt; code.length) `{`
            uint8 op = uint8(code[i]);
            if (
                op == 0x3B || // EXTCODECOPY
                op == 0x3C || // EXTCODESIZE
                op == 0x3F || // EXTCODEHASH
                op == 0x54 || // SLOAD
                op == 0x55 || // SSTORE
                op == 0xF0 || // CREATE
                op == 0xF1 || // CALL
                op == 0xF2 || // CALLCODE
                op == 0xF4 || // DELEGATECALL
                op == 0xF5 || // CREATE2
                op == 0xFA || // STATICCALL
                op == 0xFF // SELFDESTRUCT
            ) return false;

            i++;
        `}`

        return true;
    `}`

    function reverse(bytes memory a) private returns (bytes memory) `{`
        bytes memory b = new bytes(a.length);
        for (uint256 i = 0; i &lt; a.length; i++) `{`
            b[b.length - i - 1] = a[i];
        `}`
        return b;
    `}`

    function sum(bytes memory a, bytes memory b) private returns (bytes memory) `{`
        bytes memory c = new bytes(a.length);
        for (uint256 i = 0; i &lt; a.length; i++) `{`
            uint8 q = uint8(a[i]) + uint8(b[i]);
            c[i] = bytes1(q);
        `}`
        return c;
    `}`

    function deploy(bytes memory code) private returns (Storage) `{`
        require(code.length &lt;= 100);
        require(check(code));

        return Storage(address(new Dumper(code)));
    `}`

    function giveMeFlag(bytes memory code) public `{`
        Storage1 = deploy(code);
        require(Storage1.getNumber() == 1);
        Storage2 = deploy(reverse(code));
        require(Storage2.getNumber() == 2);
        Storage3 = deploy(sum(code, reverse(code)));
        require(Storage3.getNumber() == 3);

        solved = true; 
    `}`

    function isSolved() public view returns(bool) `{`
        return solved;
    `}`
`}`
```

题目需要我们通过调用 `giveMeFlag` 函数传入长度小于 `100` 的 `code` ，然后通过三个约束来通过测试，其中的三个约束分别如下：
<li>传入的 `code` 在部署后调用 `getNumber()` 函数会返回 `1`
</li>
<li>传入的 `code` 在逆序部署后调用 `getNumber()` 函数会返回 `2`
</li>
<li>将传入的 `code` 的正序和逆序的每个字节码相加并部署后调用 `getNumber()` 函数会返回 `3`
</li>
同时部署的字节码也不能够是以下的类型：

```
0x3B -&gt; EXTCODECOPY
0x3C -&gt; EXTCODESIZE
0x3F -&gt; EXTCODEHASH
0x54 -&gt; SLOAD
0x55 -&gt; SSTORE
0xF0 -&gt; CREATE
0xF1 -&gt; CALL
0xF2 -&gt; CALLCODE
0xF4 -&gt; DELEGATECALL
0xF5 -&gt; CREATE2
0xFA |-&gt; STATICCALL
0xFF -&gt; SELFDESTRUCT
```

最后函数会将 `solved` 置为 `true` ，这样当调用 `isSolved()` 方法的时候便会返回 `true` ，也就满足题目一开始所说的条件，然后我们便可以在交互处通过选项 `3` 获得 `flag`



## Code编写

在 `solidty` 中，通常的合约的入口处都是通过函数选择器来跳转到指定的方法的，具体可以参考 [CTF-wiki](https://ctf-wiki.org/blockchain/ethereum/selector-encoding/) 。然而这个函数选择器并不是必须的，交易只是会发送过来函数的签名，但是我们可以不用去检验它而直接返回。

我们可以参考 [ethervm](https://ethervm.io) 中的字节码解释来编写字节码 ，首先我们先实现一个正向的返回值为 `1` 的字节码：

```
data = ""
data += "6001" # push 01
data += "6000" # push 00
data += "52" # mstore[0:0x20] = 1
data += "6020" # push 20
data += "6000" # push 00
data += "f3" # return
print(data)
# 600160005260206000f3
```

当我们把 `600160005260206000f3` 放入 [ethervm decompile](https://ethervm.io/decompile) 中的时候，我们可以得到如下结果：

[![](https://p2.ssl.qhimg.com/t0184fa8291358b3f12.png)](https://p2.ssl.qhimg.com/t0184fa8291358b3f12.png)

这样我们便有了一个返回值恒定为 `1` 的合约。

然后以此类推，我们也可以得到一个返回值恒定为 `2` 的合约：

```
data = ""
data += "6002" # push 01
data += "6000" # push 00
data += "52" # mstore[0:0x20] = 2
data += "6020" # push 20
data += "6000" # push 00
data += "f3" # return
print(data)
# 600260005260206000f3
```

[![](https://p3.ssl.qhimg.com/t010a6fa6d89cce41a4.png)](https://p3.ssl.qhimg.com/t010a6fa6d89cce41a4.png)

当我们把第一个合约与第二个合约的逆序连起来的时候，我们就同时满足了 `giveMeFlag` 函数的两个约束条件：

```
def reverse(data):
    return bytes.fromhex(data)[::-1].hex()

data = ""
data += "6001" # push 01
data += "6000" # push 00
data += "52" # mstore[0:0x20] = 1
data += "6020" # push 20
data += "6000" # push 00
data += "f3" # return

data += "f3" # return 
data += "0060" # push 00
data += "2060" # push 20
data += "52" # mstore[0:0x20] = 2
data += "0060" # push 00
data += "0260" # push 02

print(data)
# 600160005260206000f3f3006020605200600260

print(reverse(data))
# 600260005260206000f3f3006020605200600160
```

当我们放入正序的 `data` 时效果如下：

[![](https://p4.ssl.qhimg.com/t0132944aa067faa086.png)](https://p4.ssl.qhimg.com/t0132944aa067faa086.png)

当我们放入逆序的 `data` 时效果如下：

[![](https://p1.ssl.qhimg.com/t01205d40c95e0d3c80.png)](https://p1.ssl.qhimg.com/t01205d40c95e0d3c80.png)

然而第三个约束却有些难办，其需要正序和逆序的字节码相加的字节码的合约的返回值为 `3` 。如果只是单纯的相加那肯定是不能满足约束的，在翻阅了 `solidity` [字节码](https://ethervm.io/#opcodes)的信息后，我发现可以使用 `push` 来实现将相加后的无用字节码给跳过，从而达到越过一定量的字节码来执行接下来的 `code` 的目的

[![](https://p3.ssl.qhimg.com/t014a1d31c19487af95.png)](https://p3.ssl.qhimg.com/t014a1d31c19487af95.png)

那么假如我们需要构造出相加等于 `PUSHXX` 指令的字节码，我们需要寻找一些不需要栈上数据作为输入且不怎么影响程序流程的字节码，例如：

```
0x30 -&gt; ADDRESS
0x32 -&gt; ORIGIN
0x33 -&gt; CALLER
0x34 -&gt; CALLVALUE
0x36 -&gt; CALLDATASIZE
0x38 -&gt; CODESIZE
0x3A -&gt; GASPRICE
0x3D -&gt; RETURNDATASIZE
...
```

那么我们如果构造 `PUSH11` 即 `0x6A` ，我们可以使用 `ADDRESS` 加上 `GASPRICE` ，将这两个操作码放到数据的头和尾，即可构造出一个相加起来跳过指令的字节码，然后再将返回值为 `3` 的代码加入其中，便可以构造出完整的字节码：

```
def reverse(data):
    return bytes.fromhex(data)[::-1].hex()

def combine(x,y):
    x = bytes.fromhex(x)
    y = bytes.fromhex(y)
    result = [(a + b) &amp; 0xff for a,b in zip(x,y)]
    return bytes(result).hex()

data = ""
data += "30" # ADDRESS
data += "6001" # push 01
data += "6000" # push 00
data += "52" # mstore[0:0x20] = 1
data += "6020" # push 20
data += "6000" # push 00
data += "f3" # return
data += "00" # padding

data += "6003" # push 03
data += "6000" # push 00
data += "52" # mstore[0:0x20] = 3
data += "6020" # push 20
data += "6000" # push 00
data += "f3" # return

data += "00" * 10 # padding

data += "00" # padding
data += "f3" # return 
data += "0060" # push 00
data += "2060" # push 20
data += "52" # mstore[0:0x20] = 2
data += "0060" # push 00
data += "0260" # push 02
data += "3a" # GASPRICE

print(data)
# 30600160005260206000f300600360005260206000f30000000000000000000000f30060206052006002603a

print(reverse(data))
# 3a600260005260206000f30000000000000000000000f300602060520060036000f300602060520060016030

print(combine(data,reverse(data)))
# 6ac003c000a4c040c000e600600360005260206000f3f300602060520060036000e600c040c0a400c003c06a
```

此时加起来的效果如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0131b8a7ca67626484.png)

但是如果真正将该代码放入到 `giveMeFlag()` 函数中的时候，却会提示该代码会 `revert` ，经过 `debug` 可以发现最后运行到了 `uint8 q = uint8(a[i]) + uint8(b[i]);` 语句然后进入到了 `panic_error_0x11()` 并 `revert` ，此时的 `a[i]` 和 `b[i]` 都为 `0xf3` ，所以猜测可能是整数溢出导致了这个 `revert` 。

那么该如何更改代码呢？我们可以把尾部的 `0xf3` 改为一个较小的值来错位防止加法溢出，例如改成 `03(SUB)` ，然后继续添加代码来进行下一步的修复，最后合并即可：

```
blacklist = [0x3B,0x3C,0x3F,0x54,0x55,0xF0,0xF1,0xF2,0xF4,0xF5,0xFA,0xFF]

def check(data):
    for d in data:
        if d in blacklist:
            return False
    return True

def reverse(data):
    return bytes.fromhex(data)[::-1].hex()

def combine(x,y):
    x = bytes.fromhex(x)
    y = bytes.fromhex(y)
    result = [(a + b) for a,b in zip(x,y)]
    return bytes(result).hex()

data = ""
data += "30" # ADDRESS
data += "6001" # push 01
data += "6000" # push 00
data += "52" # mstore[0:0x20] = 1
data += "6020" # push 20
data += "6000" # push 00
data += "f3" # return 

data += "00" # padding
data += "6000" # push 00

data += "6003" # push 03
data += "6000" # push 00
data += "52" # mstore[0:0x20] = 3
data += "6020" # push 20
data += "6000" # push 00
data += "f3" # return 

data += "00" * 10 # padding

data += "f3" # return 
data += "0060" # push 00
data += "03" # sub
data += "4060" # push 40
data += "2060" # push 20
data += "52" # mstore[0:0x20] = 2
data += "0060" # push 00
data += "0260" # push 02
data += "3a" # GASPRICE

if check(data):
    print(data)
# 30600160005260206000f3006000600360005260206000f300000000000000000000f30060034060206052006002603a

if check(reverse(data)):
    print(reverse(data))
# 3a600260005260206040036000f300000000000000000000f3006020605200600360006000f300602060520060016030

if check(combine(data,reverse(data))):
    print(combine(data,reverse(data)))
# 6ac003c000a4c040c040f66060f3600360005260206000f3f3006020605200600360f36060f640c040c0a400c003c06a
```

最后的正序效果如下：

[![](https://p5.ssl.qhimg.com/t018d8d297cf0eb5ab5.png)](https://p5.ssl.qhimg.com/t018d8d297cf0eb5ab5.png)

倒序效果如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a4276f7681548a7f.png)

和起来的效果如下：

[![](https://p5.ssl.qhimg.com/t013bf2480f29e6ad2a.png)](https://p5.ssl.qhimg.com/t013bf2480f29e6ad2a.png)
