> 原文链接: https://www.anquanke.com//post/id/145520 


# 代币变泡沫，以太坊Hexagon溢出漏洞比狗庄还过分


                                阅读量   
                                **176230**
                            
                        |
                        
                                                                                    



## 背景

最近通过对智能合约的审计，发现了一些智能合约相关的安全问题。其中我们发现智能合约Hexagon存在溢出攻击，可产生无数的token，导致整个代币都没有意义。

Token地址：[https://etherscan.io/address/0xB5335e24d0aB29C190AB8C2B459238Da1153cEBA](https://link.jianshu.com/?t=https%3A%2F%2Fetherscan.io%2Faddress%2F0xB5335e24d0aB29C190AB8C2B459238Da1153cEBA)

该代币可能要上交易所，我们已第一时间向官方通知该问题。

[![](https://p4.ssl.qhimg.com/t01289d9338173538ca.jpg)](https://p4.ssl.qhimg.com/t01289d9338173538ca.jpg)

目前发现受影响合约地址：

[![](https://p5.ssl.qhimg.com/dm/1024_250_/t01826c308dbe8c9040.png)](https://p5.ssl.qhimg.com/dm/1024_250_/t01826c308dbe8c9040.png)



## 成因分析

问题出现在`_transfer`函数当中，当调用`transfer`转币时，会调用`_transfer`函数：

```
/* Send tokens */
function transfer(address _to, uint256 _value) public returns (bool success) `{`
    _transfer(msg.sender, _to, _value);
    return true;
`}`
```

`_value`可控，`burnPerTransaction`为常量，当`_value + burnPerTransaction`溢出时为0，可以导致绕过验证。

```
/* INTERNAL */
function _transfer(address _from, address _to, uint _value) internal `{`
    /* Prevent transfer to 0x0 address. Use burn() instead  */
    require (_to != 0x0);
    /* Check if the sender has enough */
    require (balanceOf[_from] &gt;= _value + burnPerTransaction);
    /* Check for overflows */
    require (balanceOf[_to] + _value &gt; balanceOf[_to]);
    /* Subtract from the sender */
    balanceOf[_from] -= _value + burnPerTransaction;  
    /* Add the same to the recipient */
    balanceOf[_to] += _value;
    /* Apply transaction fee */
    balanceOf[0x0] += burnPerTransaction;
    /* Update current supply */
    currentSupply -= burnPerTransaction;
    /* Notify network */
    Burn(_from, burnPerTransaction);
    /* Notify network */
    Transfer(_from, _to, _value);
`}`
```

```
string public constant name = "Hexagon";
string public constant symbol = "HXG";
uint8 public constant decimals = 4;
uint8 public constant burnPerTransaction = 2;
```



## 漏洞利用

合约中 `burnPerTransaction` = 2 ，<br>
所以当转账`_value`为`0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe`时，<br>`_value + burnPerTransaction =0` ，即可成功攻击，为balanceOf[_to]增加大量代币。

```
require (balanceOf[_from] &gt;= _value + burnPerTransaction);   
// require (balanceOf[_from] &gt;= 0);   

[....]

require (balanceOf[_to] + _value &gt; balanceOf[_to]);   
balanceOf[_from] -= _value + burnPerTransaction;  
// balanceOf[_from]-=0
balanceOf[_to] += _value;    
//balanceOf[_to]+=fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe
```

可参考下图Transcations，目前生成的代币已销毁：<br>[![](https://p3.ssl.qhimg.com/t01a9c6676b14a907f7.jpg)](https://p3.ssl.qhimg.com/t01a9c6676b14a907f7.jpg)



## 总结

建议使用 SafeMath 来处理计算操作，避免溢出。同时，以太坊智能合约有很多开源合约，使用参考开源合约前，应对代码进行安全审计。



## 关于我们

0KEE Team隶属于360信息安全部，360信息安全部致力于保护内部安全和业务安全，抵御外部恶意网络攻击，并逐步形成了一套自己的安全防御体系，积累了丰富的安全运营和对突发安全事件应急处理经验，建立起了完善的安全应急响应系统，对安全威胁做到早发现，早解决，为安全保驾护航。技术能力处于业内领先水平，培养出了较多明星安全团队及研究员，研究成果多次受国内外厂商官方致谢，如微软、谷歌、苹果等，多次受邀参加国内外安全大会议题演讲。目前主要研究方向有区块链安全、WEB安全、移动安全（Android、iOS）、网络安全、云安全、IOT安全等多个方向，基本覆盖互联网安全主要领域。
