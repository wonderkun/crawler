> 原文链接: https://www.anquanke.com//post/id/161954 


# Not a fair game, Dice2win公平性分析


                                阅读量   
                                **122464**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t01c92d39736c8a6487.png)](https://p4.ssl.qhimg.com/t01c92d39736c8a6487.png)

> 作者：Zhiniang Peng from Qihoo 360 Core Security
Dice2win 目前是以太坊上一款异常火爆的区块链博彩游戏。号称“可证明公平的”Dice2win目前每日有近千以太(一百五十万人民币)的下注额，是总交易量仅次于etheroll的第二大以太坊博彩游戏。然而我们分析发现，dice2win中的所有游戏都存在公平性漏洞，庄家可以利用这些漏洞操纵游戏结果。

## Dice2win游戏介绍

Dice2win目前有包括“抛硬币”、“掷骰子”、“两个骰子”、“过山车”几款游戏。其介绍如图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://bjyt.s3.addops.soft.360.cn/blog/20181012/upload_1a4223259087a4e2fce8bc0329f76f5e.png)

在这些游戏中，每个用户单独下注与庄家进行一对一对赌。游戏的本质，是用户和庄家在去中心化的以太坊智能合约平台上通过一系列协议来生成随机数。如果用户猜中随机数，则用户胜利，否则庄家胜利。

在进一步介绍Dice2win工作流程和公平性分析之前，我们先讨论一个历史悠久的密码学问题：Mental poker。 Mental poker是由Shamir, Rivest和Adleman 1978年在文章“Is it possible to play a fair game of ‘Mental Poker”中首次提出的概念。(Shamir, Rivest和Adleman有没有很眼熟？没错，就是你知道的RSA)其本质是想解决：在没有可信第三方的参与的情况下(可信平台或软件)，两个不诚实的参与方如何在网络上进行一场公平的棋牌游戏。在公平性的定义中，有非常重要的一点：如果任何一方收到了游戏结果，那么所有的诚实方都应该收到结果。

Dice2win实际上是利用区块链实现mental poker的典型案例。但我们发现，Dice2win并不满足mental poker的公平性安全。



## 选择性中止攻击

这里我们来看看Dice2win的工作原理。Dice2win游戏的本质，是用户和庄家在去中心化的以太坊智能合约平台上通过一系列协议来生成随机数。如果用户猜中随机数，则用户胜利，否则庄家胜利。游戏总体工作流程如下：
1. 【庄家承诺】庄家(secretSigner)随机生成某随机数reveal，同时计算commit = keccak256 (reveal)对该reveal进行承诺。然后根据目前区块高度，设置一个该承诺使用的最后区块高度commitLastBlock。 对commitLastBlock和commit的组合体进行签名得到sig，同时把(commit, commitLastBlock,sig)发送给玩家。
1. 【玩家下注】玩家获得(commit, commitLastBlock,sig)后选择具体要玩的游戏，猜测一个随机数r，发送下注交易placeBet到智能合约上进行下注。
1. 【矿工打包】下注交易被以太坊矿工打包到区块block1中，并将玩家下注内容存储到合约存储空间中。
1. 【庄家开奖】当庄家在区块block1中看到玩家的下注信息后。则发送settleBet交易公开承诺值reveal到区块链上。合约计算随机数random_number=keccak256(reveal,block1.hash)。如果random_number满足用户下注条件，则用户胜，否则庄家胜。此外游戏还设有大奖机制，即如果某次random_number满足某个特殊值(如88888)，则用户可赢得奖金池中的大奖。
Dice2win在其官网和白皮书宣称自己的游戏具有数学上可证明的公平性，其随机数是随机数生成过程由矿工和庄家共同决定，矿工或者庄家无法左右游戏结果，所以玩家可以放心下注。此外，在一些介绍以太坊智能合约安全的文章中，我们也看到一些作者将Dice2win的随机数生成过程称为极佳实践。

然而我们分析发现，dice2win中的所有游戏都会受到庄家选择性中止攻击，庄家可以选择性公布中将结果从而导致用户无法获胜或赢得彩票。我们考虑如下两个攻击场景：

场景1：

用户下注额大，且赔率高的情况下。用户下下注产生block1后，block1.hash实际上就已经固定了。此时庄家已经可以计算出random_number，从而计算出用户的投注结果和盈亏。则庄家可以选择性中止交易。如果用户不中奖，则庄家公布正常开奖结果。如果用户中奖，则庄家可因为“网络用户和技术原因”从而导致用户该笔下注失效。

场景2：

用户下注额不大，但是block1产生后庄家发现random_number导致用户中彩票。则庄家可以选择性中止交易，导致用户该笔下注失效。

在这两种攻击场景下，庄家都能够轻松控制交易结果。当然庄家并不会对每笔交易都发起这种攻击，而是可以选择用户获奖特别大的交易进行操控。Dice2win官方实际上已经在智能合约代码得注释中声明了可能会发生“技术问题和以太坊拥堵”原因造成荷官无法开奖(大约1个小时内)，则用户可以提回下注款。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://bjyt.s3.addops.soft.360.cn/blog/20181012/upload_72b263bf5e7d2cd2ea4b2456d2e1809a.png)

造成该漏洞的本质原因在于，该方案的随机数对于庄家而言并不是真正的随机。庄家可以提前知道下注的结果。想一想如果你去一个声称“绝对公平”的赌场赌骰子。在完成下注后，庄家是有一种方法先偷看一眼骰子结果，算一算盈亏之后再决定是否开奖(重摇)，这样的骰子，是真的随机的吗？

实际上选择性中止攻击(selective abort attack)是针对mental poker公平性一种最常见的攻击方式。要修复该问题实际也很简单，只要以惩罚机制强制要求庄家在限制时间内打开承诺便可解决该问题。其他的适用于mental poker或安全多方计算的随机数生成算法均可在此处适用。



## 选择性开奖攻击

选择性中止攻击的修复实际上非常简单，要求庄家在限定时间内打开承诺便可。但这并没有从机制上完全消除Dice2win庄家在游戏中的优势。是不是简单的直接引入其他mental poker或安全多方计算的随机数生成算法到区块链智能合约平台上，就可以解决该问题了呢？实际上也未必能真正保证游戏的公平性。这里我们称述一个我们有趣的发现： 区块链智能合约上玩家交互的通讯模型，与传统的互联网用户点对点通讯模型是有区别的。传统的点对点通讯模型下证明的安全协议，直接套用到智能合约平台上未必能保证其安全性。核心原因在于：传统的点对点通讯模型下，协议的执行是顺序的，不可逆的。而智能合约的通讯模型中，由于POW等共识算法存在分叉的可能性，协议的执行可能是非顺序的可逆的。在下图中，假设黑色区块为网络主链，白色区块是分叉区块。如果一个安全多方计算的协议步骤（某笔交易）在白色执行，那么该交易将不会生效。例如Alice和Bob在区块链上进行某种计算。Alice在区块B5上执行某笔交易，Bob随后在区块B6上公布某个秘密。随后因为网络发生分叉，B5、B6上的交易都失效了。但是Alice却收到了秘密。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://bjyt.s3.addops.soft.360.cn/blog/20181012/upload_5af0756349534d263dea65b5fe9d0f92.png)

以太坊使用“幽灵协议(GHOST protocol)”来选择区块成为主链。分叉块包括叔块和孤块。下图中我们可以看到，当前以太坊叔块的概率已经达到10%以上。所以直接简单的将mental poker和安全多方计算的一些协议移植到智能合约平台上时，发生不稳定事件的概率是不可忽略的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://bjyt.s3.addops.soft.360.cn/blog/20181012/upload_684dfde59630ef367f8c0765ecce6759.png)

解决该问题的最直接的方法是，智能合约中协议的每步执行之间等待足够长的时间。当我们有接近100%把握上一个一笔交易已经在区块中稳定了，再执行下一笔交易。但这样的方式，一次交互可能要等待多个区块（数分钟的时间）才能完成。对于博彩游戏而言，显然是不可接受的。

事实上在Dice2win在上个月已经意识到叔块所带来的问题了，并声称他们的提出的MerkleProof方法可以解决该问题，从而使得游戏变得公平。并在commit中提出了使MerkleProof的方法来对叔块中的下注进行开奖（[https://github.com/dice2-win/contracts/commit/86217b39e7d069636b04429507c64dc061262d9c）。](https://github.com/dice2-win/contracts/commit/86217b39e7d069636b04429507c64dc061262d9c%EF%BC%89%E3%80%82) 现在我们看看Dice2win如何解决这个问题。在Dice2win的代码中（[https://github.com/dice2-win/contracts/blob/b0a0412f0301623dc3af2743dcace8e86cc6036b/Dice2Win.sol），我们可以看到看到方法settleBetUncleMerkleProof](https://github.com/dice2-win/contracts/blob/b0a0412f0301623dc3af2743dcace8e86cc6036b/Dice2Win.sol%EF%BC%89%EF%BC%8C%E6%88%91%E4%BB%AC%E5%8F%AF%E4%BB%A5%E7%9C%8B%E5%88%B0%E7%9C%8B%E5%88%B0%E6%96%B9%E6%B3%95settleBetUncleMerkleProof)(uint reveal, uint40 canonicalBlockNumber)：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://bjyt.s3.addops.soft.360.cn/blog/20181012/upload_47d1d4da8fe9a6e3410a3bd273b4adca.png)

Dice2win官方提出的MerkleProof方法的核心逻辑在于：为了提高用户体验（开奖速度），当荷官收到一个下注交易(Tx)的时候（假设在B5区块），就立刻计算出该下注结果并对该交易进行开奖。然而由于GHOST算法原因，最终主网选择了A5区块作为主链上的块（与B5区块hash值不同，所以开奖结果不一样）。那么此时，按合约原本SettleBet的方法是无法对B5区块进行开奖的。针对这个问题，Dice2win的解决办法是：直接对叔块进行开奖就好了。

如何对叔块进行开奖呢：因为叔块的hash是包含在主链上某个合法的区块上的。而以太坊的区块结构中又有非常多的哈希关联结构。具体我们可以看看以太坊区块头的定义：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://bjyt.s3.addops.soft.360.cn/blog/20181012/upload_200c1bdef1957b93a7f03738e5ffeab6.png)

所以我们能够从B5中交易Tx的交易执行结果Receipthash，一直计算向上层计算哈希得到叔块B5的 ReciptsRoot。然后再与其他结构进行Hash得到叔块B5的区块hash（我们称为uncleHash）。假设A6区块中引用了叔块B5的uncleHash,那么我们最终以A6的canonicalHash作为根节点，构造一个非结构性Merkle Tree。交易Tx为其中一个叶节点。其结构图如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://bjyt.s3.addops.soft.360.cn/blog/20181012/upload_a2d43a925ee0c0a7dae7721fd978a8b8.png)

Dice2win提出的Merkle proof算法的思路在于：当分叉块产生时(如同时产生B5与A5)，网络可能有两种开奖结果出现。但因为网络原因，荷官可能先收到其中一个块（假设为B5）。从荷官的视角来看，它并不知道B5是否会称为主链上的块。即使荷官多等待一段时间，收到了（A5、A6、B6）后，它仍然无法确定哪条链会称为主链。为了提高开奖速度，当荷官收到某个交易块之后，就马上进行开奖。如果该交易块最后成为主链(A5)，则正常使用SettleBet方法开奖。如果该区块最后成为叔块(B5)，则提交由该交易执行结果为叶根节点、引用该叔块的主链块canoinicalHash为根节点的非结构性Merkle tree（如上图）的一个存在性证明( Merkle proof )。从而证明B5确实存在过，且交易Tx包含在B5中；荷官可以使用叔块进行开奖。

Dice2win的Merkle proof算法看上去是一个解决以太坊上去中心化博彩游戏开奖速度的很好的思路。但实际上该做法并不公平，以太坊上接近10%的叔块率可以导致荷官以比较大的优势可以根据游戏结果进行选择性开奖。如果A5庄家赢就开A5，如果B5庄家赢就开B5。这样的方案显然不公平。



## 任意开奖攻击（Merkle proof验证绕过漏洞）

在详细阅读Dice2win关于Merkle proof的实现后，我们发现目前该合约的非结构性Merkle Proof验证存在诸多绕过方法。即荷官可以伪造一个叔块B5的Merkle proof，欺骗合约实现对任意结果进行开奖。

#### [](http://blogs.360.cn/post/Fairness_Analysis_of_Dice2win.html#toc-026)一次已经发生过的Merkle proof验证绕过攻击分析

同时，我们翻阅合约历史发现其实上个月就已经有攻击者实现了对该Merkle proof算法的绕过，将该版本的合约余额洗劫一空(但该情况为引起社区重视，Dice2win官方对该事件进行了冷处理)。在介绍我们的漏洞之前，我们可以先看看这个已发生对该Merkle proof验证算法的攻击方法。其中一笔攻击交易发生在： [https://etherscan.io/tx/0xd3b1069b63c1393b160c65481bd48c77f1d6f2b9f4bde0fe74627e42a4fc8f81](https://etherscan.io/tx/0xd3b1069b63c1393b160c65481bd48c77f1d6f2b9f4bde0fe74627e42a4fc8f81)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://bjyt.s3.addops.soft.360.cn/blog/20181012/upload_db91da5c0fb477d99cceaee06e67c771.png)

攻击者通过创建攻击合约0xc423379e42bb79167c110f4ac541c1e7c7f663d8，并在合约0xc423379e42bb79167c110f4ac541c1e7c7f663d8调用placeBet方法自动化进行下注（17次下注，每次2以太）。然后伪造Merkle proof,调用settleBetUncleMerkleProof方法开奖，在赢取了33以太后将奖金转到账户0x54b7eb670e091411f82f50fdee3743bd03384aff，最后合约自杀销毁。通过对该合约bytecode的逆向分析，我们可以得知该攻击利用了如下漏洞：
1. Dice2win不同版本的合约，存在secretSigner相同的情况。导致一个庄家的承诺可以在不同版本的合约中使用。【运维原因产生的安全漏洞】
1. placeBet方法中对commit的过期校验可被绕过。commitLastBlock与当前block.number进行大小判断时是uint256类型的。然后再带入keccak256进行签名验证的时候却转换成了uint40。那么攻击者将任意一个secretSigner签名的commitLastBlock 的最高位(256bit)从0修改为1，则可绕过时间验证。【漏洞在最新版本中仍未修复，详细见下图】
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://bjyt.s3.addops.soft.360.cn/blog/20181012/upload_2307637c78e2472f9eb3d0a87c7145b6.png)
1. Merkle proof校验不严格。在该版本的settleBetUncleMerkleProof中，每次计算hashSlot偏移的边界检查不严格(缺少32byte)，导致攻击者可以不需要将目标commit绑定到该Merkle proof的计算中，从而绕过验证。【该漏洞已修复，详见下图】
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://bjyt.s3.addops.soft.360.cn/blog/20181012/upload_226a2c4018e80e253e2b56ee6eebc955.png)

#### [](http://blogs.360.cn/post/Fairness_Analysis_of_Dice2win.html#toc-3cc)Merkle proof验证绕过漏洞

经过我们分析，Dice2win目前版本的Merkle proof仍然存在多种绕过方法。由于该方法目前只能由荷官调用，所以普通攻击者无法利用该漏洞。但该漏洞可以作为荷官后门实现任意开奖。 这里我们大致整理当前验证算法的验证逻辑：
1. 先调用requireCorrectReceipt方法校验Receipt格式满足条件。
1. Recipt trie entry中包含的是一个成功的交易。
1. 交易的目标地址是Dice2win合约。
1. Merkle Proof验证计算的起始叶节点包含目标commit。
1. 最后计算得到的canonicalHash是一个合法的主链块哈希。 条件1、2、3的满足并不是强绑定的，我们只要构造满足条件的数据格式就可以了。条件4、5的绕过，本质上是要迭代计算： hash_0=commit hash_`{`n+1`}`= SHA3(something_`{`n1`}`,hash_n,something_`{`n2`}`) canonicalHash=hash_`{`lastone`}`
攻击方法1：

一个执行成功的叔块交易中包含目标commit并不是什么难构造的事情。荷官可以在某个合约调用交易的input输入里面塞入该commit就能绕过。当然该绕过方法比较麻烦。

攻击方法2：

由于hash_`{`n+1`}`= SHA3(something_`{`n1`}`,hash_n,something_`{`n2`}`)的迭代计算未进行深度检查。所以荷官可以在本地生意一个新的merkle tree,该merkle tree的叶节点满足1、2、3条件且包含多个commit_i。将该merkle tree的根hash嵌入到一个正常的区块中，就能生成一个合法的证明。在该攻击方法中，荷官可以一劳永逸，对所有的commit进行任意开奖。

这些绕过方法的核心问题在于：目前该非结构化的Merkle tree实际上并不满足我们常说的Merkle hash tree的结构。常规的Merkle hash tree在加强限制的条件下能够进行存在性证明，但Dice2win的非结构化Merkle证明算法难以实现该目的。

#### [](http://blogs.360.cn/post/Fairness_Analysis_of_Dice2win.html#toc-550)其他安全问题：

当用户下注未被开奖，用户可以调用refundBet来溢出jackpotSize，造成jackpotSize变为一个巨大的整数(由Gaia发现并指出)。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://bjyt.s3.addops.soft.360.cn/blog/20181012/upload_aa344097d6d895cc72ebe9ae8be1acb5.png)



## 后记
1. Dice2win并不是一个公平的博彩游戏。
1. 智能合约的安全问题非常严峻。(这实际上是我分析的第一个智能合约)
1. 传统的安全多方计算的协议有时不能简单套用的到智能合约环境中，因为其通讯模型有区别。