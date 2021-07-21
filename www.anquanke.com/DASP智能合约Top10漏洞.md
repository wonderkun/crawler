> 原文链接: https://www.anquanke.com//post/id/146703 


# DASP智能合约Top10漏洞


                                阅读量   
                                **139287**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://www.dasp.co/
                                <br>原文地址：[https://www.dasp.co/](https://www.dasp.co/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0195fcc841394a7f10.png)](https://p0.ssl.qhimg.com/t0195fcc841394a7f10.png)

> 该项目是NCC集团的一项举措。这是一个开放的合作项目，致力于发现安全社区内的智能合约漏洞。
GitHub地址 [https://github.com/CryptoServices/dasp](https://github.com/CryptoServices/dasp)

在了解智能合约Top10之前，我们简单说一下，OWASP Top10。<br>
OWASP: Open Web Application Security Project

这个项目会公开十大web应用程序安全风险<br>
2017年版下载地址[http://www.owasp.org.cn/owasp-project/OWASPTop102017v1.3.pdf](http://www.owasp.org.cn/owasp-project/OWASPTop102017v1.3.pdf)

类似的，我们有了智能合约Top10漏洞。

### 以下是国外原创，翻译过来的，翻译可能不准确，还请理解。

## 

## 1.重入

也被称为或与空竞争，递归调用漏洞，未知调用等。

> 这种漏洞在很多时候被很多不同的人忽略：审阅者倾向于一次一个地审查函数，并且假定保护子例程的调用将安全并按预期运行。————菲尔戴安

### [](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#**%E9%87%8D%E5%85%A5%E6%94%BB%E5%87%BB%E4%BB%8B%E7%BB%8D**)重入攻击介绍
- 重入攻击，可能是最着名的以太坊漏洞，
- 第一次被发现时，每个人都感到惊讶。
- 它在数百万美元的抢劫案中首次亮相，导致了以太坊的分叉。
- 当初始执行完成之前，外部合同调用被允许对调用合同进行新的调用时，就会发生重新进入。
- 对于函数来说，这意味着合同状态可能会在执行过程中因为调用不可信合同或使用具有外部地址的低级函数而发生变化。
> 损失：估计为350万ETH（当时约为5000万美元）

### [](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#**%E6%94%BB%E5%87%BB%E5%8F%91%E7%8E%B0%E6%97%B6%E9%97%B4%E8%A1%A8**)攻击发现时间表

> 2016/6/5——Christian Reitwiessner发现了一个坚定的反模式<br>[https://blog.ethereum.org/2016/06/10/smart-contract-security/](https://blog.ethereum.org/2016/06/10/smart-contract-security/)

> 2016/6/9——更多以太坊攻击：Race-To-Empty是真正的交易（vessenes.com）<br>[http://vessenes.com/more-ethereum-attacks-race-to-empty-is-the-real-deal/](http://vessenes.com/more-ethereum-attacks-race-to-empty-is-the-real-deal/)

> 2016/6/12——在以太坊智能合约’递归调用’错误发现（blog.slock.it）之后，没有DAO资金面临风险。<br>[https://blog.slock.it/no-dao-funds-at-risk-following-the-ethereum-smart-contract-recursive-call-bug-discovery-29f482d348b](https://blog.slock.it/no-dao-funds-at-risk-following-the-ethereum-smart-contract-recursive-call-bug-discovery-29f482d348b)

> 2016/6/17——我认为TheDAO现在正在流失（reddit.com）<br>[https://www.reddit.com/r/ethereum/comments/4oi2ta/i_think_thedao_is_getting_drained_right_now/](https://www.reddit.com/r/ethereum/comments/4oi2ta/i_think_thedao_is_getting_drained_right_now/)

> 2016/8/24——DAO的历史和经验教训（blog.sock.it）<br>[https://blog.slock.it/the-history-of-the-dao-and-lessons-learned-d06740f8cfa5](https://blog.slock.it/the-history-of-the-dao-and-lessons-learned-d06740f8cfa5)

### [](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#**%E7%9C%9F%E5%AE%9E%E4%B8%96%E7%95%8C%E5%BD%B1%E5%93%8D**)真实世界影响

> DAO<br>[https://en.wikipedia.org/wiki/The_DAO_(organization](https://en.wikipedia.org/wiki/The_DAO_(organization))

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%A4%BA%E4%BE%8B)示例
- 一个聪明的合约跟踪一些外部地址的平衡，并允许用户通过其公共资金检索withdraw()功能。
- 一个恶意的智能合约使用withdraw()函数检索其全部余额。
- 在更新恶意合约的余额之前，受害者合约执行call.value(amount)() 低级别函数将以太网发送给恶意合约。
- 该恶意合约有一个支付fallback()接受资金的功能，然后回调到受害者合约的withdraw()功能。
- 第二次执行会触发资金转移：请记住，恶意合约的余额尚未从首次提款中更新。结果， 恶意合约第二次成功退出了全部余额。
[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B)代码示例

以下函数包含易受重入攻击影响的函数。当低级别call()函数向msg.sender地址发送ether时，它变得易受攻击; 如果地址是智能合约，则付款将触发其备用功能以及剩余的交易gas：

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E5%85%B6%E4%BB%96%E8%B5%84%E6%BA%90)其他资源

> DAO智能合约<br>[https://etherscan.io/address/0xbb9bc244d798123fde783fcc1c72d3bb8c189413#code](https://etherscan.io/address/0xbb9bc244d798123fde783fcc1c72d3bb8c189413#code)
分析DAO的利用<br>[http://hackingdistributed.com/2016/06/18/analysis-of-the-dao-exploit/](http://hackingdistributed.com/2016/06/18/analysis-of-the-dao-exploit/)
简单的DAO代码示例<br>[http://blockchain.unica.it/projects/ethereum-survey/attacks.html#simpledao](http://blockchain.unica.it/projects/ethereum-survey/attacks.html#simpledao)
重入代码示例<br>[https://github.com/trailofbits/not-so-smart-contracts/tree/master/reentrancy](https://github.com/trailofbits/not-so-smart-contracts/tree/master/reentrancy)
有人试图利用我们的智能合约中的一个缺陷，盗取它的一切<br>[https://blog.citymayor.co/posts/how-someone-tried-to-exploit-a-flaw-in-our-smart-contract-and-steal-all-of-its-ether/](https://blog.citymayor.co/posts/how-someone-tried-to-exploit-a-flaw-in-our-smart-contract-and-steal-all-of-its-ether/)

## 

## 2.访问控制

> 通过调用initWallet函数，可以将Parity Wallet库合约变为常规多sig钱包并成为它的所有者。
- 访问控制问题在所有程序中都很常见，而不仅仅是智能合约。
- 事实上，这是OWASP排名前10位的第5位。人们通常通过其公共或外部功能访问合约的功能。
- 尽管不安全的可视性设置会给攻击者直接访问合约的私有价值或逻辑的方式，但访问控制旁路有时更加微妙。
- 这些漏洞可能发生在合约使用已弃用tx.origin的验证调用者时，长时间处理大型授权逻辑require并delegatecall在代理库或代理合约中鲁莽使用。
> 损失：估计为150,000 ETH（当时约3000万美元）

### [](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#**%E7%9C%9F%E5%AE%9E%E4%B8%96%E7%95%8C%E5%BD%B1%E5%93%8D**)真实世界影响

> 奇偶校验错误1<br>[http://paritytech.io/the-multi-sig-hack-a-postmortem/](http://paritytech.io/the-multi-sig-hack-a-postmortem/)
奇偶校验错误2<br>[http://paritytech.io/a-postmortem-on-the-parity-multi-sig-library-self-destruct/](http://paritytech.io/a-postmortem-on-the-parity-multi-sig-library-self-destruct/)
Rubixi<br>[https://blog.ethereum.org/2016/06/19/thinking-smart-contract-security/](https://blog.ethereum.org/2016/06/19/thinking-smart-contract-security/)

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%A4%BA%E4%BE%8B)示例

一个聪明的合约指定它初始化它作为合约的地址。这是授予特殊特权的常见模式，例如提取合约能力。<br>
不幸的是，初始化函数可以被任何人调用，即使它已经被调用。允许任何人成为合约者并获得资金。

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B)代码示例

在下面的例子中，契约的初始化函数将函数的调用者设置为它的所有者。然而，逻辑与合约的构造函数分离，并且不记录它已经被调用的事实。

在Parity multi-sig钱包中，这个初始化函数与钱包本身分离并在“库”合约。用户需要通过调用库的函数来初始化自己的钱包delegateCall。不幸的是，在我们的例子中，函数没有检查钱包是否已经被初始化。更糟糕的是，由于图书馆是一个聪明的合约，任何人都可以自行初始化图书馆并要求销毁。

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E5%85%B6%E4%BB%96%E8%B5%84%E6%BA%90)其他资源

> 修复Parity多信号钱包bug 1<br>[https://github.com/paritytech/parity/pull/6103/files](https://github.com/paritytech/parity/pull/6103/files)
奇偶校验安全警报2<br>[http://paritytech.io/security-alert-2/](http://paritytech.io/security-alert-2/)
在奇偶钱包multi-sig hack上<br>[https://blog.zeppelin.solutions/on-the-parity-wallet-multisig-hack-405a8c12e8f7](https://blog.zeppelin.solutions/on-the-parity-wallet-multisig-hack-405a8c12e8f7)
不受保护的功能<br>[https://github.com/trailofbits/not-so-smart-contracts/tree/master/unprotected_function](https://github.com/trailofbits/not-so-smart-contracts/tree/master/unprotected_function)
Rubixi的智能合约<br>[https://etherscan.io/address/0xe82719202e5965Cf5D9B6673B7503a3b92DE20be#code](https://etherscan.io/address/0xe82719202e5965Cf5D9B6673B7503a3b92DE20be#code)

## 

## 3.算数问题

这个问题，我们之前的文章有提到，也就是比较经典的溢出。

也被称为整数溢出和整数下溢。

> 溢出情况会导致不正确的结果，特别是如果可能性未被预期，可能会影响程序的可靠性和安全性。———Jules Dourlens

溢出简介
- 整数溢出和下溢不是一类新的漏洞，但它们在智能合约中尤其危险
- 其中无符号整数很普遍，大多数开发人员习惯于简单int类型（通常是有符号整数）
- 如果发生溢出，许多良性代码路径成为盗窃或拒绝服务的载体。
### [](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%9C%9F%E5%AE%9E%E4%B8%96%E7%95%8C%E5%BD%B1%E5%93%8D)真实世界影响

> DAO<br>[http://blockchain.unica.it/projects/ethereum-survey/attacks.html](http://blockchain.unica.it/projects/ethereum-survey/attacks.html)
BatchOverflow（多个令牌）<br>[https://peckshield.com/2018/04/22/batchOverflow/](https://peckshield.com/2018/04/22/batchOverflow/)
ProxyOverflow（多个令牌）<br>[https://peckshield.com/2018/04/25/proxyOverflow/](https://peckshield.com/2018/04/25/proxyOverflow/)

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%A4%BA%E4%BE%8B)示例
- 一个聪明的合约的withdraw()功能，您可以为您的余额仍是手术后积极检索，只要捐赠合约醚。
- 一个攻击者试图收回比他或她的当前余额多。
- 该withdraw()功能检查的结果总是正数，允许攻击者退出超过允许。
- 由此产生的余额下降，并成为比它应该更大的数量级。
[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B)代码示例

最直接的例子是一个不检查整数下溢的函数，允许您撤销无限量的标记：

第二个例子（在无益的Solidity编码竞赛期间被发现[https://github.com/Arachnid/uscc/tree/master/submissions-2017/doughoyte）](https://github.com/Arachnid/uscc/tree/master/submissions-2017/doughoyte%EF%BC%89)<br>
是由于数组的长度由无符号整数表示的事实促成的错误的错误：

第三个例子是第一个例子的变体，其中两个无符号整数的算术结果是一个无符号整数：

第四个示例提供了即将弃用的var关键字。由于var将自身改变为包含指定值所需的最小类型，因此它将成为uint8保持值0.如果循环的迭代次数超过255次，它将永远达不到该数字，并且在执行运行时停止出gas：

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E5%85%B6%E4%BB%96%E8%B5%84%E6%BA%90)其他资源

> SafeMath防止溢出<br>[https://ethereumdev.io/safemath-protect-overflows/](https://ethereumdev.io/safemath-protect-overflows/)
整数溢出代码示例<br>[https://github.com/trailofbits/not-so-smart-contracts/tree/master/integer_overflow](https://github.com/trailofbits/not-so-smart-contracts/tree/master/integer_overflow)

## 

## 4.未检查返回值的低级别调用

也称为或与无声失败发送， 未经检查发送。

> 应尽可能避免使用低级别“呼叫”。如果返回值处理不当，它可能会导致意外的行为。——Remix

其中的密实度的更深层次的特点是低级别的功能call()，callcode()，delegatecall()和send()。他们在计算错误方面的行为与其他Solidity函数完全不同，因为他们不会传播（或冒泡），并且不会导致当前执行的全部回复。相反，他们会返回一个布尔值设置为false，并且代码将继续运行。这可能会让开发人员感到意外，如果未检查到这种低级别调用的返回值，则可能导致失败打开和其他不想要的结果。请记住，发送可能会失败！

### [](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%9C%9F%E5%AE%9E%E4%B8%96%E7%95%8C%E5%BD%B1%E5%93%8D)真实世界影响

> <p>以太之王——[https://www.kingoftheether.com/postmortem.html](https://www.kingoftheether.com/postmortem.html)<br>
Etherpot——[https://www.dasp.co/](https://www.dasp.co/)</p>

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B)代码示例
- 下面的代码是一个当忘记检查返回值时会出错的例子send()。
- 如果调用用于将ether发送给不接受它们的智能合约（例如，因为它没有应付回退功能）
- 则EVM将用其替换其返回值false。
- 由于在我们的例子中没有检查返回值，因此函数对合约状态的更改不会被恢复，并且etherLeft变量最终会跟踪一个不正确的值：
[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E5%85%B6%E4%BB%96%E8%B5%84%E6%BA%90)其他资源

> 未经检查的外部电话<br>[https://github.com/trailofbits/not-so-smart-contracts/tree/master/unchecked_external_call](https://github.com/trailofbits/not-so-smart-contracts/tree/master/unchecked_external_call)
扫描“未经检查 – 发送”错误的现场以太坊合约<br>[http://hackingdistributed.com/2016/06/16/scanning-live-ethereum-contracts-for-bugs/](http://hackingdistributed.com/2016/06/16/scanning-live-ethereum-contracts-for-bugs/)



## 5.拒绝服务

包括达到气量上限，意外抛出，意外杀死，访问控制违规

> I accidentally killed it. ————devops199 on the Parity multi-sig wallet
- 在以太坊的世界中，拒绝服务是致命的：
- 尽管其他类型的应用程序最终可以恢复，但智能合约可以通过其中一种攻击永远脱机。
- 许多方面导致拒绝服务，包括在作为交易接受方时恶意行为
- 人为地增加计算功能所需的gas，滥用访问控制访问智能合约的私人组件
- 利用混淆和疏忽，…这类攻击包括许多不同的变体，并可能在未来几年看到很多发展。
> 损失：估计为514,874 ETH（当时约3亿美元）

### [](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%9C%9F%E5%AE%9E%E4%B8%96%E7%95%8C%E5%BD%B1%E5%93%8D)真实世界影响

> 政府<br>[https://www.reddit.com/r/ethereum/comments/4ghzhv/governmentals_1100_eth_jackpot_payout_is_stuck/](https://www.reddit.com/r/ethereum/comments/4ghzhv/governmentals_1100_eth_jackpot_payout_is_stuck/)
奇偶校验多信号钱包<br>[http://paritytech.io/a-postmortem-on-the-parity-multi-sig-library-self-destruct/](http://paritytech.io/a-postmortem-on-the-parity-multi-sig-library-self-destruct/)

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%A4%BA%E4%BE%8B)示例
- 一个拍卖合约允许它的用户出价不同的资产。
- 为了投标，用户必须bid(uint object)用期望的以太数来调用函数。
- 拍卖合约将把以太保存在第三方保存中，直到对象的所有者接受投标或初始投标人取消。
- 这意味着拍卖合约必须在其余额中保留未解决出价的全部价值。
- 该拍卖合约还包括一个withdraw(uint amount)功能，它允许管理员从合约获取资金。
- 随着函数发送amount到硬编码地址，开发人员决定公开该函数。
- 一个攻击者看到了潜在的攻击和调用功能，指挥所有的合约的资金为其管理员。
- 这破坏了托管承诺并阻止了所有未决出价。
- 虽然管理员可能会将托管的钱退还给合约，但攻击者可以通过简单地撤回资金继续进行攻击。
[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B)代码示例

在下面的例子中（受以太王的启发[http://blockchain.unica.it/projects/ethereum-survey/attacks.html#kotet）](http://blockchain.unica.it/projects/ethereum-survey/attacks.html#kotet%EF%BC%89)<br>
游戏合约的功能可以让你成为总统，如果你公开贿赂前一个。不幸的是，如果前总统是一个聪明的合约，并导致支付逆转，权力的转移将失败，恶意智能合约将永远保持总统。听起来像是对我的独裁：

在第二个例子中，调用者可以决定下一个函数调用将奖励谁。由于for循环中有昂贵的指令，攻击者可能会引入太大的数字来迭代（由于以太坊中的气体阻塞限制），这将有效地阻止函数的功能。

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E5%85%B6%E4%BB%96%E8%B5%84%E6%BA%90)其他资源

> 奇偶Multisig被黑客入侵。再次<br>[https://medium.com/chain-cloud-company-blog/parity-multisig-hack-again-b46771eaa838](https://medium.com/chain-cloud-company-blog/parity-multisig-hack-again-b46771eaa838)
关于Parity multi-sig钱包漏洞和Cappasity令牌众包的声明<br>[https://blog.artoken.io/statement-on-the-parity-multi-sig-wallet-vulnerability-and-the-cappasity-artoken-crowdsale-b3a3fed2d567](https://blog.artoken.io/statement-on-the-parity-multi-sig-wallet-vulnerability-and-the-cappasity-artoken-crowdsale-b3a3fed2d567)

## 

## 6.错误随机

也被称为没有什么是秘密的

> 合约对block.number年龄没有足够的验证，导致400个ETH输给一个未知的玩家，他在等待256个街区之前揭示了可预测的中奖号码。—————阿森尼罗托夫
- 以太坊的随机性很难找到。
- 虽然Solidity提供的功能和变量可以访问明显难以预测的值
- 但它们通常要么比看起来更公开，要么受到矿工影响。
- 由于这些随机性的来源在一定程度上是可预测的，所以恶意用户通常可以复制它并依靠其不可预知性来攻击该功能。
> 损失：超过400 ETH

### [](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%9C%9F%E5%AE%9E%E4%B8%96%E7%95%8C%E5%BD%B1%E5%93%8D)真实世界影响

> SmartBillions彩票<br>[https://www.reddit.com/r/ethereum/comments/74d3dc/smartbillions_lottery_contract_just_got_hacked/](https://www.reddit.com/r/ethereum/comments/74d3dc/smartbillions_lottery_contract_just_got_hacked/)
TheRun<br>[https://medium.com/@hrishiolickel/why-smart-contracts-fail-undiscovered-bugs-and-what-we-can-do-about-them-119aa2843007](https://medium.com/@hrishiolickel/why-smart-contracts-fail-undiscovered-bugs-and-what-we-can-do-about-them-119aa2843007)

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%A4%BA%E4%BE%8B)示例
1. 甲智能合约使用块号作为随机有游戏用的源。
1. 攻击者创建一个恶意合约来检查当前的块号码是否是赢家。如果是这样，它就称为第一个智能合约以获胜; 由于该呼叫将是同一交易的一部分，因此两个合约中的块编号将保持不变。
1. 攻击者只需要调用她的恶意合同，直到获胜。
[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B)代码示例

在第一个例子中，a private seed与iteration数字和keccak256散列函数结合使用来确定主叫方是否获胜。Eventhough的seed是private，它必须是通过交易在某个时间点设置，并因此在blockchain可见。
- 在这第二个例子中，block.blockhash正被用来生成一个随机数。
- 如果将该哈希值blockNumber设置为当前值block.number（出于显而易见的原因）并且因此设置为，则该哈希值未知0。
- 在blockNumber过去设置为超过256个块的情况下，它将始终为零。
- 最后，如果它被设置为一个以前的不太旧的区块号码，另一个智能合约可以访问相同的号码并将游戏合约作为同一交易的一部分进行调用。
[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E5%85%B6%E4%BB%96%E8%B5%84%E6%BA%90)其他资源

> 在以太坊智能合约中预测随机数<br>[https://blog.positive.com/predicting-random-numbers-in-ethereum-smart-contracts-e5358c6b8620](https://blog.positive.com/predicting-random-numbers-in-ethereum-smart-contracts-e5358c6b8620)
在以太坊随机<br>[https://blog.otlw.co/random-in-ethereum-50eefd09d33e](https://blog.otlw.co/random-in-ethereum-50eefd09d33e)

## 

## 7.前台运行

也被称为检查时间与使用时间（TOCTOU），竞争条件，事务顺序依赖性（TOD）

> 事实证明，只需要150行左右的Python就可以获得一个正常运行的算法。————Ivan Bogatyy
- 由于矿工总是通过代表外部拥有地址（EOA）的代码获得gas费用
- 因此用户可以指定更高的费用以便更快地开展交易。
- 由于以太坊区块链是公开的，每个人都可以看到其他人未决交易的内容。
- 这意味着，如果某个用户正在揭示拼图或其他有价值的秘密的解决方案，恶意用户可以窃取解决方案并以较高的费用复制其交易，以抢占原始解决方案。
- 如果智能合约的开发者不小心，这种情况会导致实际的和毁灭性的前端攻击。
### [](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%9C%9F%E5%AE%9E%E4%B8%96%E7%95%8C%E5%BD%B1%E5%93%8D)真实世界影响

> Bancor<br>[https://hackernoon.com/front-running-bancor-in-150-lines-of-python-with-ethereum-api-d5e2bfd0d798](https://hackernoon.com/front-running-bancor-in-150-lines-of-python-with-ethereum-api-d5e2bfd0d798)
ERC-20<br>[https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/](https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/)
TheRun<br>[https://www.dasp.co/](https://www.dasp.co/)

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%A4%BA%E4%BE%8B)示例
1. 一个聪明的合约发布的RSA号（N = prime1 x prime2）。
1. 对其submitSolution()公共功能的调用与权利prime1并prime2奖励来电者。
1. Alice成功地将RSA编号考虑在内，并提交解决方案。
1. 有人在网络上看到Alice的交易（包含解决方案）等待被开采，并以较高的gas价格提交。
1. 由于支付更高的费用，第二笔交易首先被矿工收回。该攻击者赢得奖金。
[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E5%85%B6%E4%BB%96%E8%B5%84%E6%BA%90)其他资源

> 在以太坊智能合约中预测随机数<br>[https://blog.positive.com/predicting-random-numbers-in-ethereum-smart-contracts-e5358c6b8620](https://blog.positive.com/predicting-random-numbers-in-ethereum-smart-contracts-e5358c6b8620)
虚拟和解的前卫，悲痛和危险<br>[https://blog.0xproject.com/front-running-griefing-and-the-perils-of-virtual-settlement-part-1-8554ab283e97](https://blog.0xproject.com/front-running-griefing-and-the-perils-of-virtual-settlement-part-1-8554ab283e97)
Frontrunning Bancor<br>[https://www.youtube.com/watch?v=RL2nE3huNiI](https://www.youtube.com/watch?v=RL2nE3huNiI)

## 

## 8.时间操纵

也被称为时间戳依赖

> 如果一位矿工持有合约的股份，他可以通过为他正在挖掘的矿区选择合适的时间戳来获得优势。———-Nicola Atzei，Massimo Bartoletti和Tiziana Cimoli
- 从锁定令牌销售到在特定时间为游戏解锁资金，合约有时需要依赖当前时间。
- 这通常通过Solidity中的block.timestamp别名或其别名完成now。
- 但是，这个价值从哪里来？来自矿工！
- 由于交易的矿工在报告采矿发生的时间方面具有回旋余地
- 所以良好的智能合约将避免强烈依赖所宣传的时间。
- 请注意，block.timestamp有时（错误）也会在随机数的生成中使用，如＃6所述。坏随机性。
### [](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%9C%9F%E5%AE%9E%E4%B8%96%E7%95%8C%E5%BD%B1%E5%93%8D)真实世界影响

> 政府<br>[http://blockchain.unica.it/projects/ethereum-survey/attacks.html#governmental](http://blockchain.unica.it/projects/ethereum-survey/attacks.html#governmental)

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%A4%BA%E4%BE%8B)示例
1. 一场比赛在今天午夜付出了第一名球员。
1. 恶意的矿工包括他或她试图赢得比赛并将时间戳设置为午夜。
1. 在午夜之前，矿工最终挖掘该块。当前的实时时间“足够接近”到午夜（当前为该块设置的时间戳），网络上的其他节点决定接受该块。
[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B)代码示例

以下功能只接受特定日期之后的呼叫。由于矿工可以影响他们区块的时间戳（在一定程度上），他们可以尝试挖掘一个包含他们交易的区块，并在未来设定一个区块时间戳。如果足够接近，它将在网络上被接受，交易将在任何其他玩家试图赢得比赛之前给予矿工以太：

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E5%85%B6%E4%BB%96%E8%B5%84%E6%BA%90)其他资源

> 对以太坊智能合约的攻击调查<br>[https://eprint.iacr.org/2016/1007](https://eprint.iacr.org/2016/1007)
在以太坊智能合约中预测随机数<br>[https://blog.positive.com/predicting-random-numbers-in-ethereum-smart-contracts-e5358c6b8620](https://blog.positive.com/predicting-random-numbers-in-ethereum-smart-contracts-e5358c6b8620)
让智能合约变得更聪明<br>[https://blog.acolyer.org/2017/02/23/making-smart-contracts-smarter/](https://blog.acolyer.org/2017/02/23/making-smart-contracts-smarter/)

## 

## 9.短地址攻击

也被称为或涉及非连锁问题，客户端漏洞

> 为令牌传输准备数据的服务假定用户将输入20字节长的地址，但实际上并未检查地址的长度。—-PawełBylica
- 短地址攻击是EVM本身接受不正确填充参数的副作用。
- 攻击者可以通过使用专门制作的地址来利用这一点，使编码错误的客户端在将它们包含在事务中之前不正确地对参数进行编码。
- 这是EVM问题还是客户问题？是否应该在智能合约中修复？
- 尽管每个人都有不同的观点，但事实是，这个问题可能会直接影响很多以太网。
- 虽然这个漏洞还没有被大规模利用，但它很好地证明了客户和以太坊区块链之间的交互带来的问题。
- 其他脱链问题存在：重要的是以太坊生态系统对特定的javascript前端，浏览器插件和公共节点的深度信任。
- 臭名昭着的链外利用被用于Coindash ICO的黑客在他们的网页上修改了公司的以太坊地址，诱骗参与者将ethers发送到攻击者的地址。
### [](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E5%8F%91%E7%8E%B0%E6%97%B6%E9%97%B4%E8%A1%A8)发现时间表
- 2017/4/6————如何通过阅读区块链来找到1000万美元
- [https://blog.golemproject.net/how-to-find-10m-by-just-reading-blockchain-6ae9d39fcd95](https://blog.golemproject.net/how-to-find-10m-by-just-reading-blockchain-6ae9d39fcd95)
### [](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%9C%9F%E5%AE%9E%E4%B8%96%E7%95%8C%E5%BD%B1%E5%93%8D)真实世界影响

> 未知交换（s）<br>[https://blog.golemproject.net/how-to-find-10m-by-just-reading-blockchain-6ae9d39fcd95](https://blog.golemproject.net/how-to-find-10m-by-just-reading-blockchain-6ae9d39fcd95)

[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E7%A4%BA%E4%BE%8B)示例
1. 交易所API具有交易功能，可以接收收件人地址和金额。
1. 然后，API transfer(address _to, uint256 _amount)使用填充参数与智能合约函数进行交互：它将12位零字节的地址（预期的20字节长度）预先设置为32字节长
1. Bob（0x3bdde1e9fbaef2579dd63e2abbf0be445ab93f00）要求Alice转让他20个代币。他恶意地将她的地址截断以消除尾随的零。
1. Alice使用交换API和Bob（0x3bdde1e9fbaef2579dd63e2abbf0be445ab93f）的较短的19字节地址。
1. API用12个零字节填充地址，使其成为31个字节而不是32个字节。有效地窃取以下_amount参数中的一个字节。
1. 最终，执行智能合约代码的EVM将会注意到数据未被正确填充，并会在_amount参数末尾添加丢失的字节。有效地传输256倍以上的令牌。
[](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E5%85%B6%E4%BB%96%E8%B5%84%E6%BA%90)其他资源

> ERC20短地址攻击说明<br>[http://vessenes.com/the-erc20-short-address-attack-explained/](http://vessenes.com/the-erc20-short-address-attack-explained/)
分析ERC20短地址攻击<br>[https://ericrafaloff.com/analyzing-the-erc20-short-address-attack/](https://ericrafaloff.com/analyzing-the-erc20-short-address-attack/)
智能合约短地址攻击缓解失败<br>[https://blog.coinfabrik.com/smart-contract-short-address-attack-mitigation-failure/](https://blog.coinfabrik.com/smart-contract-short-address-attack-mitigation-failure/)
从标记中删除短地址攻击检查<br>[https://github.com/OpenZeppelin/zeppelin-solidity/issues/261](https://github.com/OpenZeppelin/zeppelin-solidity/issues/261)

## 

## 10.未知的未知物

> 我们相信更多的安全审计或更多的测试将没有什么区别。主要问题是评审人员不知道要寻找什么。———Christoph Jentzsch
- 以太坊仍处于起步阶段。
- 用于开发智能合约的主要语言Solidity尚未达到稳定版本
- 而生态系统的工具仍处于试验阶段。
- 一些最具破坏性的智能合约漏洞使每个人都感到惊讶
- 并且没有理由相信不会有另一个同样出乎意料或同样具有破坏性的漏洞。
- 只要投资者决定将大量资金用于复杂而轻微审计的代码
- 我们将继续看到新发现导致可怕后果。
- 正式验证智能合约的方法尚不成熟，但它们似乎具有很好的前景，可以作为摆脱今天不稳定现状的方式。
- 随着新类型的漏洞不断被发现，开发人员需要继续努力
- 并且需要开发新工具来在坏人之前找到它们。
- 这个Top10可能会迅速发展，直到智能合约开发达到稳定和成熟的状态。
## [](/myblog/%E5%8C%BA%E5%9D%97%E9%93%BE/dasptop10.html#%E5%8E%9F%E6%96%87%E5%9C%B0%E5%9D%80)
