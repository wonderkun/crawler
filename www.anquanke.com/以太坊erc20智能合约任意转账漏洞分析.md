> 原文链接: https://www.anquanke.com//post/id/146010 


# 以太坊erc20智能合约任意转账漏洞分析


                                阅读量   
                                **143708**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                    



## [![](https://p1.ssl.qhimg.com/t018943b94be0743a88.jpg)](https://p1.ssl.qhimg.com/t018943b94be0743a88.jpg)

## 漏洞描述



## 漏洞影响

昨天，经过360智能合约平台监控发现，edu代币存在交易异常，经过分析发现，其智能合约transferFrom函数存在问题，导致攻击者可以转走任意用户的代币，最后经过分析发现包括EDU在内总共有7个智能合约存在相同的问题，其代币合约地址:

1.0x81f074bb3b158bf81799dcff159521a089e59a37

2.0x6ec0a0901715e0d015fd775e5dfddd7f2de0308e

3.0x87be146d2e2d2ae71a83895a3ad15c66546af5e2

4.0xf270f361edca19f7063184b0e6b4f264468ecbc1

5.0x0156888f51d68f858ac88aba45df699e2af2e4cc    VRT

6.0x14d9779b6585f3a7d4f768383b3cb030705dad2e   BAI

7.0xa0872ee815b8dd0f6937386fd77134720d953581   EDU

其中**前四个**合约已经很久没有交易，基本废弃。目前还在交易的，影响比较大的是**后三个**代币。

以EDU代币为例，我们可以看到较近交易数据中存在大额交易异常，如下图所示：

[![](https://p2.ssl.qhimg.com/t01d31947779967e068.png)](https://p2.ssl.qhimg.com/t01d31947779967e068.png)



## 漏洞成因

经过分析发现EDU代币的transferFrom函数中,allowed[from][msg.sender]减去要转账的数字时候，没有对比allowed[from][msg.sender]的值与value的值得大小，从而使得可以转走比allowed[from][msg.sender]大的数目的代币。

[![](https://p1.ssl.qhimg.com/t016e13dc292fdb282e.png)](https://p1.ssl.qhimg.com/t016e13dc292fdb282e.png)



## 如何避免这个问题

经过对这些合约的分析，我们发现基本上合约开发人员会去校验blances[from]的值,而对allowed[from][msg.sender]的校验却忽略了,合约开发者开发者应该去选择调用更安全的safemath库函数来进行数字运算操作，防止任意转账的操作。



## 关于我们

360作为全球最大互联网安全企业，致力于提供区块链相关安全解决方案，为区块链行业客户及互联网用户提供安全保障。
