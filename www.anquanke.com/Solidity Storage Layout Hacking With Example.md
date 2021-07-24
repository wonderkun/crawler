> 原文链接: https://www.anquanke.com//post/id/188464 


# Solidity Storage Layout Hacking With Example


                                阅读量   
                                **669837**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01bde62693fa68569d.jpg)](https://p5.ssl.qhimg.com/t01bde62693fa68569d.jpg)

> 关于storage的layout，之前只是记着，真正要用的时候就有点分析不清楚了，这儿专门总结一下，并结合例子，加深记忆

## Basic Principles
- 静态型的变量，即除去mapping以及动态数组外，都是连续从storage地址0开始的。**这里切忌和memory**搞混
- 单元基本都是32bytes一个slot (32 bytes 即 256 bit，可以说是最大单元如`int256`)
<li>对于小于 32bytes 的变量，可以尝试依照如下规则来“挤”
<ol>
- 第一个成员要对齐到低端
- 基本类型只占用其所需要空间对应的bytes
- 如果该slot空间不足以放入当前元素，则起到下一个slot中
- 结构体或者数组一定会新起一个slot，但结构体和数组内成员也按如上规则压紧在一起
</ol>
</li>
接下来不妨看个例子

### <a class="reference-link" name="%E4%BE%8B1"></a>例1

```
pragma solidity ^0.4.18;
contract example1 `{`
    int var0;
    address var1;
    address private var2;
    bytes4  constant var3 = 0x12345678;
    bytes4  var4;
    bytes12 var5;

    function init () public `{`
        var0 = 0x01;
        var1 = 0x79F7f5116f58A91f0D88520ef4B8034b5019525B;
        var2 = 0x6146feF6760831eba2d3f8B841553837f985b4fd;
        var4 = 0x3456789a;
        var5 = 0x13579bdf2468ace066666666;
    `}`
`}`
```

我们定义了6个变量，并其中`var3`加了`private`修饰，`var4`加了const修饰，且这6个均是**elementary type**，我们先构想一下其分布应该如下所指示

```
SLOTS0[0: 32] = var0;
SLOTS1[0: 20] = var1;
SLOTS2[0: 20] = var2;
SLOTS2[21:24] = var3;
SLOTS2[25:28] = var4;
SLOTS3[0: 12] = var5;
```

是不是这样呢，我们用[remix](https://remix.ethereum.org/)调试一下，我们部署好后就可以看到下图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://pz15tf70k.bkt.clouddn.com/2019-10-11-Solidy-Storage-Layout-With-Example-first.png)

很真实的看到，var3变量没有前导0，var4变量有刚好4个字节的前导零，这自然就是`SLOTS2`没用到的部分，我们的预估正确

> 官方文档中有专门的警告，提及到**When using elements that are smaller than 32 bytes, your contract’s gas usage may be higher**，看样子不能为了省空间用小变量，而是要注意一些技巧如: declaring your storage variables in the order of uint128, uint128, uint256 instead of uint128, uint256, uint128, as the former will only take up two slots of storage whereas the latter will take up three.



## Advanced principle

首先我们想一想结构体，其实一个结构体单元的空间是可以预知的，所以其特殊就在于新起一个slot,其他我们按旧规则推理即可；

可是对于空间不确定的(mapping以及动态数组)，我们就需要额外的tricks

`mapping`结构或者动态数组其本身单元需要占据一个空的slot(按之前提到的顺序找)，我们指代其为**p**；对于动态数组，这里会存储动态数组的长度(byte array和字符串属于例外，后续讨论)，而对于映射，这个单元并不显示地存放值，但需要**p**参与哈希的计算。对，关键就是哈希！

数组的整体会从`keccak256(p)`开始，顺序存放，同之前所提到的，这一部分整体会按照规则**compacted**排列。<br>
而对于键值为**k**的映射单元来说，其对应的元素会存放到`keccak256(k.p)`位置，这里`.`是**concatenation**，注意，如果元素又不是一个**Elementary type**的话，则通过加上`keccak256(k.p)`的偏移值去找；

是不是有点绕了，我们看例子就好

### <a class="reference-link" name="%E4%BE%8B2"></a>例2

```
pragma solidity ^0.4.18;

contract example2 `{`
    int[] array1;
    bytes4[] array2; 

    function init () public `{`
        int item1 = 1;
        array1.push(item1);
        array1.push(item1 + 1);
        bytes4 item2 = 0x12345678;
        array2.push(item2);
        array2.push(0x12345679);
    `}`
`}`
```

数组的测试我们就快速过一下，对应单元存放的是长度，代码执行完后两个数组应该是双元素

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://pz15tf70k.bkt.clouddn.com/2019-10-11-Solidy-Storage-Layout-With-Example-second.png)

对于`array1`，其两元素的分布起始地址应该是`keccak256(0)`

可以找个[在线的计算网站](http://juan.blanco.ws/SHA3/)帮忙算，或者用`pyethereum`的包更方便一些

> 千万注意了，前面的表述稍有误差，严格来说不是`keccak256(0)`而是`keccak256(x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00)`，不然就会错❌，试了好久

如下图是array1，计算符合预期

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://pz15tf70k.bkt.clouddn.com/2019-10-11-Solidy-Storage-Layout-With-Example-third.png)

如下图是array2，果然把bytes4合并到了一个slots中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://pz15tf70k.bkt.clouddn.com/2019-10-11-Solidy-Storage-Layout-With-Example-forth.png)

哦你可能会奇怪，在**key**和**value**对上面那个奇怪的串对应的啥？这个我们留到后面一点解释。<br>
数组的情况还是容易理解，接下来我们看映射

### <a class="reference-link" name="%E4%BE%8B3"></a>例3

```
pragma solidity ^0.4.18;

contract example3 `{`
    mapping(address=&gt;uint) balance;

    function deposit (uint id) public payable`{`
        balance[id] += msg.value / (1 ether);
    `}`
`}`
```

这次我们通过逆向来看看咋回事

```
function deposit() `{`
        memory[0x00:0x20] = msg.sender;
        memory[0x20:0x40] = 0x00;
        var temp0 = keccak256(memory[0x00:0x40]);
        storage[temp0] = msg.value / 0x0de0b6b3a7640000 + storage[temp0];
`}`
```

通过逆向工具，发现目标地址计算是将键值与对应的`p`连接起来后哈希运算得到，很好理解～

### <a class="reference-link" name="%E7%BB%BC%E5%90%88"></a>综合

我们找个大一点的合约来好好分析一下地址分布

```
pragma solidity ^0.4.24;

contract Bank `{`
    event SendEther(address addr);
    event SendFlag(address addr);

    address public owner;
    uint randomNumber = 0;

    constructor() public `{`
        owner = msg.sender;
    `}`

    struct SafeBox `{`
        bool done;
        function(uint, bytes12) internal callback;
        bytes12 hash;
        uint value;
    `}`
    SafeBox[] safeboxes;

    struct FailedAttempt `{`
        uint idx;
        uint time;
        bytes12 triedPass;
        address origin;
    `}`
    mapping(address =&gt; FailedAttempt[]) failedLogs;

    modifier onlyPass(uint idx, bytes12 pass) `{`
        if (bytes12(sha3(pass)) != safeboxes[idx].hash) `{`
            FailedAttempt info;
            info.idx = idx;
            info.time = now;
            info.triedPass = pass;
            info.origin = tx.origin;
            failedLogs[msg.sender].push(info);
        `}`
        else `{`
            _;
        `}`
    `}`

    function deposit(bytes12 hash) payable public returns(uint) `{`
        SafeBox box;
        box.done = false;
        box.hash = hash;
        box.value = msg.value;
        if (msg.sender == owner) `{`
            box.callback = sendFlag;
        `}`
        else `{`
            require(msg.value &gt;= 1 ether);
            box.value -= 0.01 ether;
            box.callback = sendEther;
        `}`
        safeboxes.push(box);
        return safeboxes.length-1;
    `}`

    function withdraw(uint idx, bytes12 pass) public payable `{`
        SafeBox box = safeboxes[idx];
        require(!box.done);
        box.callback(idx, pass);
        box.done = true;
    `}`

    function sendEther(uint idx, bytes12 pass) internal onlyPass(idx, pass) `{`
        msg.sender.transfer(safeboxes[idx].value);
        emit SendEther(msg.sender);
    `}`

    function sendFlag(uint idx, bytes12 pass) internal onlyPass(idx, pass) `{`
        require(msg.value &gt;= 100000000 ether);
        emit SendFlag(msg.sender);
        selfdestruct(owner);
    `}`

`}`
```

这是才不久之前的`Balsn CTF`的一道智能合约题目，当时因为不可抗原因导致无法做，后期我会出一篇专文来讲，这里我们只是分析一下storage的layout

首先，我们把storage变量列一下
- address public owner := 占据 SLOTS0[0: 20]
- uint randomNumber := 占据 SLOTS1[0: 32]
- SafeBox[] safeboxes := 结构体动态数组，其中 SLOTS2 保留数组长度
- mapping(address =&gt; FailedAttempt[]) failedLogs := 嵌套动态数组的映射
前两个较为简单，结构体动态数组主要注重偏移，但较为复杂的就是嵌套动态数组的mapping<br>
首先，SLOTS3为其留空，因为其本质是一个映射，当进入`onlyPass`函数并触发`failedLogs[msg.sender].push(info);`时，我们理一理，首先**key value**是**msg.sender**，这说明对应的动态数组的长度会保存到`keccak(msg.sender.3)`处。

而数组元素则递归的，即第一个元素值（注意这个值是结构体哦）应该是存放到`keccak(keccak(msg.sender.3))`这，并连续的向下延展

如果感觉有点不明白，建议读者用Remix操作试一试，毕竟纸上得来终觉浅，绝知此事要躬行



## 参考

[Layout of State Variables in Storage](https://solidity.readthedocs.io/en/v0.4.24/miscellaneous.html#layout-of-state-variables-in-storage)
