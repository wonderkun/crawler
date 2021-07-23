> 原文链接: https://www.anquanke.com//post/id/101682 


# 如何使用Go语言编写自己的区块链挖矿算法


                                阅读量   
                                **84611**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Coral Health，文章来源：medium.com
                                <br>原文地址：[https://medium.com/@mycoralhealth/code-your-own-blockchain-mining-algorithm-in-go-82c6a71aba1f](https://medium.com/@mycoralhealth/code-your-own-blockchain-mining-algorithm-in-go-82c6a71aba1f)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0149c7a383ca459215.png)](https://p0.ssl.qhimg.com/t0149c7a383ca459215.png)



## 一、前言

随着近期比特币（Bitcoin）以及以太坊（Ethereum）挖矿热潮的兴起，人们很容易对此浮想联翩。对于刚进入该领域的新手而言，他们会听到各种故事，比如许多人将GPU堆满仓库来疯狂挖矿，每月能挖到价值数百万美元的加密货币（cryptocurrency）。那么就是什么是密币挖矿？挖矿的原理是什么？怎么样才能编写自己的挖矿算法？

在本文中，我们会给大家一一解答这些问题，然后介绍如何编写自己的挖矿算法。我们将这种算法称为**Proof of Work**（工作量证明）算法，该算法是比特币及以太坊这两种最流行的加密货币的基础。无需担忧，我们会给大家介绍得明明白白。



## 二、什么是密币挖矿

物以稀为贵，对加密货币来说也是如此。如果任何人在任何时间都可以随意生产任意多的比特币，那么比特币作为一种货币则毫无价值可言（稍等，这不正是美联储常干的事吗……）。比特币算法每隔10分钟就会向比特币网络中的获胜成员颁发一次比特币，总量大约在122年内会达到最大值。这种颁发机制可以将通货膨胀率控制在一定范围内，因为算法并没有在一开始就给出所有密币，而是随着时间推移逐步产出。

在这种算法下，为了获取比特币奖励，矿工们需要付出“劳动”，与其他矿工竞争。这个过程也称为“挖矿”，因为该过程类似于黄金矿工的采矿过程，为了找到一点黄金，工人们也需要付出时间及精力最终才能获取胜利果实（有时候也会竹篮打水一场空）。

比特币算法会强制参与者（或节点）进行挖矿，同时相互竞争，确保比特币产出速度不至于太快。



## 三、如何挖矿

如果在Google上搜索“如何挖比特币？”，我们会看到大量结果，纷纷解释挖掘比特币需要节点（用户或者主机）来解决复杂的[数学难题](https://www.bitcoinmining.com/)。虽然这种说法从技术角度来看没有问题，但简单称之为“数学”问题显然有点太过于僵硬，挖矿的过程其实非常有趣。我们要了解一些密码学知识以及哈希算法，才能理解挖矿的原理。

### <a class="reference-link" name="%E5%AF%86%E7%A0%81%E5%AD%A6%E7%AE%80%E4%BB%8B"></a>密码学简介

单向加密以人眼可读的数据作为输入（如“Hello world”），然后通过某个函数生成难以辨认的输出。这些函数（或者算法）在性质及复杂度上各不相同。算法越复杂，想逆向分析就越难。因此，加密算法在保护数据（如用户密码以及军事代码）方面至关重要。

以非常流行的SHA-256算法为例，我们可以使用[哈希生成网站](http://www.xorbin.com/tools/sha256-hash-calculator)来生成SHA-256哈希值。比如，我们可以输入“Hello world”，观察对应的哈希结果：

[![](https://p3.ssl.qhimg.com/t01f2e2efa45cbe80f9.png)](https://p3.ssl.qhimg.com/t01f2e2efa45cbe80f9.png)

我们可以重复计算“Hello world”的哈希值，每次都能得到相同的结果。在编程中，输入相同的情况下，如果每次都得到同样的输出，这个过程称之为“幂等性（idempotency）”。

对于加密算法而言，我们很难通过逆向分析来推导原始输入，但很容易验证输出结果是否正确，这是加密算法的一个基本特性。比如前面那个例子，我们很容易就能验证“Hello world”的SHA-256哈希值是否正确，但很难通过给定的哈希值来推导原始输入为“Hello world”。这也是我们为何将这类加密方法称为单向加密的原因所在。

比特币使用的是双重SHA-256算法（Double SHA-256）,也就是说它会将“Hello world”的SHA-256哈希值作为输入，再计算一次SHA-256哈希。在本文中，为了方便起见，我们只计算一次SHA-256哈希。

### <a class="reference-link" name="%E6%8C%96%E7%9F%BF"></a>挖矿

理解加密算法后，我们可以回到密币挖矿这个主题上。比特币需要找到一些方法，让希望获得比特币的参与者能通过加密算法来“挖矿”，以便控制比特币的产出速度。具体说来，比特币会让参与者计算一堆字母和数字的哈希值，直到他们算出的哈希值中“前导0”的位数超过一定长度为止。

比如，回到前面那个[哈希计算网站](http://www.xorbin.com/tools/sha256-hash-calculator)，输入“886”后我们可以得到前缀为3个0的哈希值。

[![](https://p3.ssl.qhimg.com/t01b56f5d32faa6c692.png)](https://p3.ssl.qhimg.com/t01b56f5d32faa6c692.png)

问题是我们如何才能知道“886”的哈希值开头包含3个零呢？这才是重点。在撰写本文之前，我们没有办法知道这一点。从理论上讲，我们必须尝试字母和数字的各种组合，对结果进行测试，直到获得满足要求的结果为止。这里我们事先给出了“886”的哈希结果以便大家理解。

任何人都能很容易验证出“886”是否会生成3位前导零的哈希结果，这样就能证明我们的确做了大量测试、检查了大量字母和数字的组合，最终得到了这一结果。因此，如果我们是第一个获得这个结果的人，其他人可以快速验证“886”的正确性，这个工作量的证明过程可以让我赢得比特币。这也是为什么人们把比特币的一致性算法称之为Proof-of-Work（工作量证明）算法。

但如果我的运气爆表，第一次尝试就生成了3个前导零结果呢？这种事情基本不可能发生，偶然的节点在首次尝试时就成功挖掘新块（向大家证明他们的确做了这项工作）的可能性微乎其微，相反其他数百万个节点需要付出大量工作才能找到所需的散列。你可以继续尝试一下，随便输入一些字母和数字的组合，我打赌你得不到3个前导零的结果。

比特币的约束条件比这个例子更加复杂（要求得到更多位前导零！），并且它能动态调整难度，以确保工作量不会太轻或者太重。请记住，比特币算法的目标是每隔10分钟产出一枚比特币。因此，如果太多人参与挖矿，比特币需要加大工作量证明难度，实现难度的动态调整。从我们的角度来看，调整难度等同于增加更多位前导零。

因此，大家可以明白比特币的一致性算法比单纯“解决数学难题”要有趣得多。



## 四、开始编程

背景知识已经介绍完毕，现在我们可以使用Proof-of-Work算法来构建自己的区块链（Blockchain）程序。我选择使用Go语言来实现，这是一门[非常棒](https://hackernoon.com/5-reasons-why-we-switched-from-python-to-go-4414d5f42690)的语言。

在继续之前，我建议你阅读我们之前的一篇博客：&lt;a href=”https://medium.com/[@mycoralhealth](https://github.com/mycoralhealth)/code-your-own-blockchain-in-less-than-200-lines-of-go-e296282bcffc”&gt;《用200行Go代码实现自己的区块链》。这不是硬性要求，但我们会快速掠过以下某些例子，如果你想了解更多细节，可以参考那篇文章。如果你已经了如指掌，可以直接跳到“Proof of Work”章节。

整体架构如下：

[![](https://p3.ssl.qhimg.com/t01bc5b6360c91e0008.png)](https://p3.ssl.qhimg.com/t01bc5b6360c91e0008.png)

我们需要一台Go服务器，为了简单起见，我会将所有代码放在一个`main.go`文件中。这个文件提供了关于区块链逻辑的所有信息（包括Proof of Work），也包含所有REST API对应的处理程序。区块链数据是不可改变的，我们只需要`GET`以及`POST`请求即可。我们需要使用浏览器发起GET请求来查看数据，使用[Postman](https://www.getpostman.com/apps)来`POST`新的区块（也可以使用`curl`）。

### <a class="reference-link" name="%E5%AF%BC%E5%85%A5%E4%BE%9D%E8%B5%96"></a>导入依赖

首先我们需要导入一些库，请使用`go get`命令获取如下包：

1、`github.com/davecgh/go-spew/spew`：帮助我们在终端中直接查看结构规整的区块链信息。

2、`github.com/gorilla/mux`：用来搭建Web服务器的一个库，非常好用。

3、`github.com/joho/godotenv`：可以从根目录中的`.env`文件中读取环境变量。

首先我们可以在根目录中创建一个`.env`文件，用来存放后面需要的一个环境变量。`.env`文件只有一行：`ADDR=8080`。

在根目录的`main.go`中，将依赖包以声明的方式导入：

```
package main

import (
        "crypto/sha256"
        "encoding/hex"
        "encoding/json"
        "fmt"
        "io"
        "log"
        "net/http"
        "os"
        "strconv"
        "strings"
        "sync"
        "time"

        "github.com/davecgh/go-spew/spew"
        "github.com/gorilla/mux"
        "github.com/joho/godotenv"
)
```

如果你看过我们前面那篇&lt;a href=”https://medium.com/[@mycoralhealth](https://github.com/mycoralhealth)/code-your-own-blockchain-in-less-than-200-lines-of-go-e296282bcffc”&gt;文章，那么对下面这张图应该不会感到陌生。我们使用散列算法来验证区块链中区块的正确性，具体方法是将某个区块中的**previous hash**与前一个区块的**hash**进行对比，确保两者相等。这样就能维护区块链的完整性，并且恶意成员无法篡改区块链的历史信息。

[![](https://p5.ssl.qhimg.com/t015875bd51f2429908.png)](https://p5.ssl.qhimg.com/t015875bd51f2429908.png)

其中，`BPM`指的是脉搏速率，或者每分钟的跳动次数。我们将使用你的心率来作为区块中的一部分数据。你可以将两根手指放在手腕内侧，计算一分钟内感受到多少次脉动，记住这个数字即可。

### <a class="reference-link" name="%E5%9F%BA%E6%9C%AC%E6%A6%82%E5%BF%B5"></a>基本概念

现在，在`main.go`的声明语句后面添加数据模型以及后面需要用到的其他变量。

```
const difficulty = 1

type Block struct `{`
        Index      int
        Timestamp  string
        BPM        int
        Hash       string
        PrevHash   string
        Difficulty int
        Nonce      string
`}`

var Blockchain []Block

type Message struct `{`
        BPM int
`}`

var mutex = &amp;sync.Mutex`{``}`
```

`difficulty`是一个常量，用来定义哈希值中需要的前导零位数。前导零位数越多，我们越难找到正确的哈希值。我们先从1位前导零开始。

`Block`是每个区块的数据模型。不要担心`Nonce`字段，后面我们会介绍。

`Blockchain`由多个`Block`组成，代表完整的区块链。

我们会在REST API中，使用`POST`请求提交`Message`以生成新的`Block`。

我们声明了一个互斥量`mutex`，后面我们会使用该变量避免出现数据竞争，确保多个区块不会同一时间生成。

### <a class="reference-link" name="Web%E6%9C%8D%E5%8A%A1%E5%99%A8"></a>Web服务器

让我们快速搭一个Web服务器。首先创建一个`run`函数，`main`函数随后会调用这个函数来运行服务器。我们在`makeMuxRouter()`中声明了相应的请求处理函数。请注意，我们需要通过`GET`请求获取区块链，通过`POST`请求添加新的区块。区块链无法更改，因此我们不需要实现编辑或删除功能。

```
func run() error `{`
        mux := makeMuxRouter()
        httpAddr := os.Getenv("ADDR")
        log.Println("Listening on ", os.Getenv("ADDR"))
        s := &amp;http.Server`{`
                Addr:           ":" + httpAddr,
                Handler:        mux,
                ReadTimeout:    10 * time.Second,
                WriteTimeout:   10 * time.Second,
                MaxHeaderBytes: 1 &lt;&lt; 20,
        `}`

        if err := s.ListenAndServe(); err != nil `{`
                return err
        `}`

        return nil
`}`

func makeMuxRouter() http.Handler `{`
        muxRouter := mux.NewRouter()
        muxRouter.HandleFunc("/", handleGetBlockchain).Methods("GET")
        muxRouter.HandleFunc("/", handleWriteBlock).Methods("POST")
        return muxRouter
`}`
```

`httpAddr := os.Getenv("ADDR")`这行语句会从我们前面创建的`.env`文件中提取`:8080`这个信息。我们可以通过浏览器访问`http://localhost:8080/`这个地址来访问我们构建的应用。

现在我们需要编写`GET`处理函数，在浏览器中显示区块链信息。我们还需要添加一个`respondwithJSON`函数，一旦API调用过程中出现错误就能以JSON格式返回错误信息。

```
func handleGetBlockchain(w http.ResponseWriter, r *http.Request) `{`
        bytes, err := json.MarshalIndent(Blockchain, "", "  ")
        if err != nil `{`
                http.Error(w, err.Error(), http.StatusInternalServerError)
                return
        `}`
        io.WriteString(w, string(bytes))
`}`

func respondWithJSON(w http.ResponseWriter, r *http.Request, code int, payload interface`{``}`) `{`
        w.Header().Set("Content-Type", "application/json")
        response, err := json.MarshalIndent(payload, "", "  ")
        if err != nil `{`
                w.WriteHeader(http.StatusInternalServerError)
                w.Write([]byte("HTTP 500: Internal Server Error"))
                return
        `}`
        w.WriteHeader(code)
        w.Write(response)
`}`
```

**请注意：如果觉得我们讲得太快，可以参考之前的&lt;a href=”https://medium.com/[@mycoralhealth](https://github.com/mycoralhealth)/code-your-own-blockchain-in-less-than-200-lines-of-go-e296282bcffc”&gt;文章，文章中详细解释了每个步骤。**

现在编写`POST`处理函数，这个函数可以实现新区块的添加过程。我们使用Postman来发起`POST`请求，向`http://localhost:8080`发送JSON数据（如``{`“BPM”:60`}``），其中包含前面你记录下的那个脉搏次数。

```
func handleWriteBlock(w http.ResponseWriter, r *http.Request) `{`
        w.Header().Set("Content-Type", "application/json")
        var m Message

        decoder := json.NewDecoder(r.Body)
        if err := decoder.Decode(&amp;m); err != nil `{`
                respondWithJSON(w, r, http.StatusBadRequest, r.Body)
                return
        `}`   
        defer r.Body.Close()

        //ensure atomicity when creating new block
        mutex.Lock()
        newBlock := generateBlock(Blockchain[len(Blockchain)-1], m.BPM)
        mutex.Unlock()

        if isBlockValid(newBlock, Blockchain[len(Blockchain)-1]) `{`
                Blockchain = append(Blockchain, newBlock)
                spew.Dump(Blockchain)
        `}`   

        respondWithJSON(w, r, http.StatusCreated, newBlock)

`}`
```

请注意代码中`mutex`的lock以及unlock操作。在写入新的区块之前，我们需要锁定互斥量，不然多次写入就会造成数据竞争。细心的读者会注意到`generateBlock`函数，这是处理Proof of Work的关键函数，稍后我们会介绍。

### <a class="reference-link" name="%E5%9F%BA%E6%9C%AC%E7%9A%84%E5%8C%BA%E5%9D%97%E9%93%BE%E5%87%BD%E6%95%B0"></a>基本的区块链函数

在介绍Proof of Work之前，先整理下基本的区块链函数。我们添加了一个`isBlockValid`函数，确保我们的索引能正确递增，并且当前区块的`PrevHash`与前一个区块的`Hash`相匹配。

我们也添加了一个`calculateHash`函数，用来生成哈希值，以计算`Hash`以及`PrevHash`。我们将`Index`、`Timestamp`、`BPM`、`PrevHash`以及`Nonce`（稍后我们会介绍这个字段）串在一起，计算出一个SHA-256哈希。

```
func isBlockValid(newBlock, oldBlock Block) bool `{`
        if oldBlock.Index+1 != newBlock.Index `{`
                return false
        `}`

        if oldBlock.Hash != newBlock.PrevHash `{`
                return false
        `}`

        if calculateHash(newBlock) != newBlock.Hash `{`
                return false
        `}`

        return true
`}`

func calculateHash(block Block) string `{`
        record := strconv.Itoa(block.Index) + block.Timestamp + strconv.Itoa(block.BPM) + block.PrevHash + block.Nonce
        h := sha256.New()
        h.Write([]byte(record))
        hashed := h.Sum(nil)
        return hex.EncodeToString(hashed)
`}`
```



## 五、Proof of Work

现在来介绍挖矿算法，也就是Proof of Work。在新的`Block`加入`blockchain`之前，我们需要确保Proof of Work任务已经完成。我们先以一个简单的函数开始，该函数可以检查Proof of Work过程中生成的哈希是否满足我们设置的约束条件。

我们的约束条件如下：

1、Proof of Work生成的哈希必须具有特定位数的前导零。

2、前导零的位数由程序刚开始定义的`difficulty`常量来决定（这里这个值为1）.

3、我们可以增加难度值来提高Proof of Work的难度。

首先构造一个函数：`isHashValid`：

```
func isHashValid(hash string, difficulty int) bool `{`
        prefix := strings.Repeat("0", difficulty)
        return strings.HasPrefix(hash, prefix)
`}`
```

Go语言在`strings`包中提供了`Repeat`以及`HasPrefix`函数，使用起来非常方便。我们定义了一个`prefix`变量，用来表示前导零位数，然后检查哈希值的前导零位数是否满足要求，满足则返回`True`，不满足则返回`False`。

接下来创建`generateBlock`函数。

```
func generateBlock(oldBlock Block, BPM int) Block `{`
        var newBlock Block

        t := time.Now()

        newBlock.Index = oldBlock.Index + 1
        newBlock.Timestamp = t.String()
        newBlock.BPM = BPM
        newBlock.PrevHash = oldBlock.Hash
        newBlock.Difficulty = difficulty

        for i := 0; ; i++ `{`
                hex := fmt.Sprintf("%x", i)
                newBlock.Nonce = hex
                if !isHashValid(calculateHash(newBlock), newBlock.Difficulty) `{`
                        fmt.Println(calculateHash(newBlock), " do more work!")
                        time.Sleep(time.Second)
                        continue
                `}` else `{`
                        fmt.Println(calculateHash(newBlock), " work done!")
                        newBlock.Hash = calculateHash(newBlock)
                        break
                `}`

        `}`
        return newBlock
`}`
```

我们创建了一个`newBlock`变量，将前一个区块的哈希值保存到`PrevHash`字段中，确保区块链满足连续性要求。其他字段的含义应该比较明显：

1、`Index`不断增加；

2、`Timestamp`是当前时间的字符串表现形式；

3、`BPM`是前面记录下的心率；

4、`Difficulty`直接摘抄自最开头定义的那个常量。这个例子中我们不会使用这个字段，但如果我们想进一步验证，确保难度值与哈希结果一致（也就是说哈希结果的前导零位数为N，那么`Difficulty`的值应该也为N，否则区块链就会遭到破坏），那么这个字段就非常有用。

这个函数中的`for`循环非常重要，我们详细介绍一下：

1、获取`i`的十六进制形式，将该值赋给`Nonce`。我们需要一种方法来将动态变化的一个值加入哈希结果中，这样如果我们没有得到理想的哈希值，就可以通过`calculateHash`函数继续生成新的值。我们在`calculateHash`计算过程中添加的动态值就称为“Nonce”。

2、在循环中，我们的`i`和Nonce值从0开始递增，判断生成的哈希结果中前导零位数是否与`difficulty`相等。如果不相等，我们进入新的迭代，增加Nonce，再次计算。

3、我们加了1秒的休眠操作，模拟解决Proof of Work所需的时间。

4、继续循环，直到计算结果中包含特定位数的前导零为止，此时我们成功完成了Proof of Work任务。只有在这种情况下，我们的`Block`才能通过`handleWriteBlock`处理函数添加到`blockchain`中。

现在我们已经完成了所有函数，因此让我们完成`main`函数吧：

```
func main() `{`
        err := godotenv.Load()
        if err != nil `{`
                log.Fatal(err)
        `}`   

        go func() `{`
                t := time.Now()
                genesisBlock := Block`{``}`
                genesisBlock = Block`{`0, t.String(), 0, calculateHash(genesisBlock), "", difficulty, ""`}` 
                spew.Dump(genesisBlock)

                mutex.Lock()
                Blockchain = append(Blockchain, genesisBlock)
                mutex.Unlock()
        `}`() 
        log.Fatal(run())

`}`
```

使用`godotenv.Load()`语句我们可以完成环境变量（`:8080`端口）的加载，以便通过浏览器进行访问。

区块链得有一个起点，所以我们使用一个go例程来创建创世区块。

然后使用前面构造的`run()`函数启动Web服务器。



## 六、大功告成

大家可以访问[Github](https://github.com/mycoralhealth/blockchain-tutorial/blob/master/proof-work/main.go)获取完整版代码。

来跑一下看看效果。

首先使用`go run main.go`命令启动程序。

然后在浏览器中访问`http://localhost:8080`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c84fd118420854c6.png)

区块链中已经有一个创世区块。现在打开Postman，通过POST请求向服务器发送包含BPM字段（心率数据）的JSON数据。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012bcd878863d187f6.png)

发送完请求后，我们可以在终端中观察操作结果。可以看到，我们的计算机会使用不断递增的Nonce值来创建新的哈希，直到计算出来的哈希满足前导零位数要求为止。

[![](https://p3.ssl.qhimg.com/t01a9e5a4f71058ca1d.png)](https://p3.ssl.qhimg.com/t01a9e5a4f71058ca1d.png)

完成Proof of Work任务后，我们可以看到一则提示消息：`work done!`。我们可以检验这个哈希值，发现它的确满足`difficulty`所设置的前导零位数要求。这意味着从理论上来讲，我们使用`BPM = 60`参数所生成的新区块现在应该已经添加到区块链中。

刷新浏览器看一下结果：

[![](https://p3.ssl.qhimg.com/t019b1144066eaeb35a.png)](https://p3.ssl.qhimg.com/t019b1144066eaeb35a.png)

大功告成！我们的第二个区块已经添加到创世区块后面。也就是说，我们成功通过`POST`请求发送了区块，这个操作触发了挖矿过程，当且仅当Proof of Work得以解决时，新的区块才能添加到区块链中。



## 七、下一步考虑

非常好，前面学到的知识非常重要。Proof of Work是比特币、以太坊以及其他区块链平台的基础。我们前面的分析意义非凡，虽然这个例子使用的难度值并不大，但实际环境中Proof of Work区块链的工作原理就是把难度提高到较高水平而已。

现在你已经深入了解了区块链技术的关键组成部分，后面的路需要你自己去走，我们建议你可以继续学习以下知识：

1、学习区块链网络的工作原理，可以参考我们的&lt;a href=”https://medium.com/[@mycoralhealth](https://github.com/mycoralhealth)/part-2-networking-code-your-own-blockchain-in-less-than-200-lines-of-go-17fe1dad46e1″&gt;网络教程。

2、学习如何以分布式方式存储大型文件并与区块链交互，可以参考我们的&lt;a href=”https://medium.com/[@mycoralhealth](https://github.com/mycoralhealth)/learn-to-securely-share-files-on-the-blockchain-with-ipfs-219ee47df54c”&gt;IPFS教程。

如果你还想继续深入学习，可以考虑了解一下Proof of Stake（权益证明）。尽管目前大多数区块链使用Proof of Work作为一致性算法，但公众越来越关注Proof of Stake。人们普遍认为，未来以太坊将从Proof of Work迁移至Proof of Stake。
