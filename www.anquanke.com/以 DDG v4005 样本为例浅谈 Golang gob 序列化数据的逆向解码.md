> 原文链接: https://www.anquanke.com//post/id/192948 


# 以 DDG v4005 样本为例浅谈 Golang gob 序列化数据的逆向解码


                                阅读量   
                                **1010520**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01dc235c3a946c25c4.jpg)](https://p0.ssl.qhimg.com/t01dc235c3a946c25c4.jpg)



## 1. 概述

DDG 是一个 一直活跃的挖矿僵尸网络，其主样本由 Go 语言编写。它最新活跃的版本中用基于 Gossip 协议实现集群管理的第三方库 **[Memberlist](https://github.com/hashicorp/memberlist)** 把整个僵尸网络构建成了一个非典型的 P2P 结构。关于其 P2P 网络结构以及如何基于 P2P 特性追踪该僵尸网络，我在以前的两篇文章中有详细描述：
1. [以P2P的方式追踪 DDG 僵尸网络(上)](https://www.anquanke.com/post/id/177665)
1. [以P2P的方式追踪 DDG 僵尸网络(下)](https://www.anquanke.com/post/id/177742)
11.6 日晚上，我的 DDG 挖矿僵尸网络追踪程序检测到 DDG 家族更新到了版本 4005，IoC 如下：

> **MD5:**
<ul>
- 64c6692496110c0bdce7be1bc7cffd47 ddgs.i686
- 638061d2a06ebdfc82a189cf027d8136 ddgs.x86_64
</ul>
**CC**:
<ul>
- 67.207.95[.]103:8000
- 103.219.112[.]66:8000
</ul>

经过简单的分析，新版恶意样本的关键行为与旧版本差异不大，以前部署的追踪程序依然能持续追踪。不过其中一个小的技术点引起了我的注意。

以前说过，DDG 样本为了通过 Memberlist 库加入 P2P 网络(函数 `Memberlist.join()`)，需要一批初始的 P2P Nodes ，新的样本代表的 P2P 节点会通过这些初始的 P2P Nodes 加入 P2P 网络。在旧版样本中，这些初始的 P2P Nodes 被称为 **Hub List**，其中约有 200 个 节点 IP 地址，这一份 IP 列表以 Hex 数组形式硬编码保存在样本中。而新版 DDG 样本中则把这些 P2P Nodes 称为 **Seeds**(Memberlist 库 `Join()` 函数的 ”种子“)，这些 Seeds 用 [Golang gob](https://blog.golang.org/gobs-of-data) 序列化编码后再硬编码保存在样本中，样本里还用一组 `ddgs_network__mlUtils_*` 函数来处理这些 Seeds：

[![](https://p2.ssl.qhimg.com/t012379bdeacc3e1b9c.png)](https://p2.ssl.qhimg.com/t012379bdeacc3e1b9c.png)

对于旧版样本的做法，定位到 Hub List 数据后，在 IDAPro 中逆向分析样本时直接用 IDAPython 脚本将 Hex 形式的 IP 地址转成点分十进制表示即可一目了然把这些 IP 提取出来，但新版样本中这些数据被 gob 序列化编码过，该怎么提取？



## 2. gob 序列化编码

gob(**Go Binary** 的简称)，是 Go 语言自带的序列化编码方案，用法简洁，灵活性和效率很高，也有一定的扩展性。可以类比 Python 的 Pickle，用来对结构化数据进行序列化编解码以方便数据传输。由于 gob 是 Go 独有的，并没有现成的 Python 接口，所以想用 Python 在 IDAPro 中直接解码不太现实，就只好手动把编码过的二进制数据从样本中 Dump 出来，然后写 Go 程序来解码。

使用 gob 对数据编码，一般是发送端针对已定义好结构的数据进行编码后发送；接收端收到二进制数据后，按照与发送端**兼容**的数据结构进行解码(不一定是完全相同的结构定义，但数据类型以及数量要兼容发送端的数据结构定义，这个 **兼容** 则体现了 gob 的灵活性)。一个简单的数据结构如下所示：

```
type S struct `{`
    X, Y, Z int
    Name    string
    L       []string
`}`
```

所以，要逆向分析经 gob 序列化编码过的数据，对数据进行精准解码，最大的难点在于逆向出 Go 语言形式的数据结构定义。

gob 的用法不是本文重点，可以参考[官方介绍](https://blog.golang.org/gobs-of-data) 与这一篇[中文详解](https://www.bitlogs.tech/2019/08/go-encoding/gob/) 。



## 3. 恶意样本中的数据解码过程

以样本 ddgs.x86_64(MD5: **638061d2a06ebdfc82a189cf027d8136**) 为例，在函数 `ddgs_network__mlUtils_JoinAll()` 中，通过对 `Memberlist.Join()` 函数的调用，即可顺藤摸瓜找到数据解码以及转换的函数：

[![](https://p4.ssl.qhimg.com/t014966a6c0b9fc1158.png)](https://p4.ssl.qhimg.com/t014966a6c0b9fc1158.png)

最上面的 `ddgs_network__mlUtils_Seeds()` 函数中，可以看到样本中经 gob 序列化编码的数据地址与长度，样本先是读取这一段数据，然后用 gob 进行解码：

[![](https://p2.ssl.qhimg.com/t01a164266a392ea9d4.png)](https://p2.ssl.qhimg.com/t01a164266a392ea9d4.png)

在 IDAPro 中逆向分析样本，无法还原数据的结构定义。我们把这段数据手动 Dump 出来看看：

[![](https://p1.ssl.qhimg.com/t0164e134c973b3921e.png)](https://p1.ssl.qhimg.com/t0164e134c973b3921e.png)

可以看到高亮的两个字段名：**IP** 和 **Port**。到这里就有点灵感了，我们再看看解密后的数据是如何使用的，就能看出这些数据到底是什么结构了。在函数 `ddgs_network__mlUtils_Seeds()` 中继续往下看，会发现样本为了把这些 Seed Nodes 列表输出到日志中，用 `ddgs_network__mlUtils_Seeds_func1()` 函数把解密后的数据做了解析、重组：

[![](https://p1.ssl.qhimg.com/t01a7b147ec5a3a435c.png)](https://p1.ssl.qhimg.com/t01a7b147ec5a3a435c.png)

在函数`ddgs_network__mlUtils_Seeds_func1()` 中，样本内部把解密后的数据以循环处理的方式，依次调用 `ddgs_network__seedNode_Address()` 函数来解析成字符串，并把每个代表 Seed Node 的字符串用竖线 **|** 连接起来：

[![](https://p4.ssl.qhimg.com/t01a7efbd4a6de836fe.png)](https://p4.ssl.qhimg.com/t01a7efbd4a6de836fe.png)

看来逆向出数据结构定义的关键就是 `ddgs_network__seedNode_Address()` 函数函数了：

[![](https://p3.ssl.qhimg.com/t01ef4009cc24c6a1b2.png)](https://p3.ssl.qhimg.com/t01ef4009cc24c6a1b2.png)

可以看到 `ddgs_network__seedNode_Address()` 函数中，对每一个 Seed Node 对象都做两部分处理：第一个成员是用 Go 标准库 `net.IP.String()` 函数将 `net.IP` 对象转化为 String 类型；第二个成员是直接转化为 64bit 整型值。最后将 String 类型的 IP 地址与整型的 Port 值串成一个 `IP:Port` 结构的字符串来代表一个 Seed Node。

这正好跟前文用 Hexdump 查看 Raw 二进制数据里的两个字段 **IP** 和 **Port** 对上了。

至此，我们就可以断定，这些 gob 编码数据的**基础结构定义**应该如下所示：

```
import "net"

type SeedNode struct `{`
    IP   net.IP
    Port int64
`}`
```



## 4. 完成数据解码

上面我们分析出了编码数据原始的**基础结构定义**，之所以说是**基础**，是因为这个结构定义只代表**单个 Seed Node**，而这些数据是**一批 Seed Node** 的列表。要想写程序完成最终的数据解码，还需要用 Go 的数组或切片把上面的数据结构定义封装一下。最终的数据解码代码关键部分示例如下：

```
type SeedNode struct `{`
    IP   net.IP
    Port int64
`}`

// Open the dumped raw data file
fd, fdErr := os.OpenFile("raw_data.dump", os.O_RDONLY, 0644)
br := bufio.NewReader(fd)

dec := gob.NewDecoder(br)

// make Seed Node slice
var d []SeedNode
decErr := dec.Decode(&amp;d)

for _, seedNode := range d `{`
    fmt.Printf("%s:%dn", seedNode.IP, seedNode.Port)
`}`
```

完整代码链接： [https://github.com/0xjiayu/decode_gob_in_ddgs_v4005/blob/master/hubs_dump.go](https://github.com/0xjiayu/decode_gob_in_ddgs_v4005/blob/master/hubs_dump.go)



## 5. 辅助工具——degob

DDG v4005 的样本中涉及的 gob 数据编码，原始数据结构简单，逆向难度不高。如果遇到结构更复杂的数据经 gob 序列化编码，逆向难度肯定要增加。如果有一款工具可以自动化把任意 gob 序列化后的数据还原，最好不过了。

Google 一番，我找到了一个还算理想的工具，degob，专为逆向分析 gob 编码数据而生： [https://gitlab.com/drosseau/degob](https://gitlab.com/drosseau/degob)

不过 degob 并不完美，它只能解析出 Go 最底层的数据类型。比如本文中用到的 `net.IP`，定义为：

```
type IP []byte
```

那么 degob 解析数据的时候，就会把 `net.IP` 这一个成员表示为 `[]byte`，至于这个 `[]byte` 的**高层结构类型**代表什么，还需要结合样本逆向来确认。比如我逆向时发现样本中用 `net.IP.String()` 函数来解析这个数据成员，那么就可以确定，degob 解析出来的 `[]byte` ，其实就是 `net.IP`。degob 解析上述 Raw Data，得出的数据结构定义为：

```
// []Anon65_5e8660ee

// type ID: 65
type Anon65_5e8660ee struct `{`
        IP []byte
        Port int64
`}`
```

然后就是 degob 解出来的部分数据(不完美解析，需要结合样本逆向才能确认 IP 的真实结构类型)：

[![](https://p2.ssl.qhimg.com/t013dd3054c569c3a4e.png)](https://p2.ssl.qhimg.com/t013dd3054c569c3a4e.png)

不过，这个 degob 两年没更新了，作者可能也不维护了，在它的 **cmds/degob/main.go** 文件中还有一个 Bug，命令行参数把 **inFile** 误写成了 **outFile** ：

[![](https://p0.ssl.qhimg.com/t01eba802087430b20d.png)](https://p0.ssl.qhimg.com/t01eba802087430b20d.png)



## 6. 总结

DDG 的恶意样本中还有另外一个序列化数据的解码，即用 [msgPack](https://msgpack.org/) 编码的云端配置数据。如果要用 msgPack 的 Go 语言 SDK 去解码这个配置文件，需要逆向分析出更复杂的配置数据结构定义(在 [以P2P的方式追踪 DDG 僵尸网络(下)](https://www.anquanke.com/post/id/177742) 一文中有详细阐述)。不过好在 msgPack 是个通用的序列化编码方案，除了 Go，还支持其他语言，比如 Python。更方便的是，用 msgPack for Python 来对序列化数据进行解码并不需要预先知道数据结构定义即可直接解码，这就大大降低了逆向工作的难度。

然而 gob 序列化只属于 Go 语言自有，并没有其他语言的 SDK，要想逆向解码 gob 序列化编码过的二进制数据数据，就必须分析出原始的数据结构定义。这样来看， gob 序列化数据逆向解码并没有万全之策，即使有 degob 这种工具的加持，也得结合样本逆向分析才能精准解析、还原明文数据。

本文用到的 Go 语言程序、从样本中提取的 gob 编码的原始二进制数据以及样本运行时的 debug 日志，都上传到 Github，感兴趣的师傅自取：

[https://github.com/0xjiayu/decode_gob_in_ddgs_v4005](https://github.com/0xjiayu/decode_gob_in_ddgs_v4005)
