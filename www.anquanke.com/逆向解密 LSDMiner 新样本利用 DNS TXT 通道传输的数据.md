> 原文链接: https://www.anquanke.com//post/id/193116 


# 逆向解密 LSDMiner 新样本利用 DNS TXT 通道传输的数据


                                阅读量   
                                **1187237**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t014163ec85e179770f.jpg)](https://p2.ssl.qhimg.com/t014163ec85e179770f.jpg)



## 1. 概述

10 月中旬，部门老司机发给我一个 LSDMiner(旧称 **Watchdogsminer**) 最新活动中的一个样本(MD5: 114d76b774185b826830cb6b015cb56f)。当时大概看了一眼，里面用到了 DNS TXT 记录来传输经过 AES 加密的数据，手头忙别的事，就先搁下了。近来捡起来分析，Google 搜索样本中用到的一个函数 **NewAesCipher128()** ，发现国外安全公司 **Anomali** 已经分析过这个 Case ：

[![](https://p0.ssl.qhimg.com/t016be9c7fae6c30516.png)](https://p0.ssl.qhimg.com/t016be9c7fae6c30516.png)

Anomali 的 Blog： [Illicit Cryptomining Threat Actor Rocke Changes Tactics, Now More Difficult to Detect](https://www.anomali.com/blog/illicit-cryptomining-threat-actor-rocke-changes-tactics-now-more-difficult-to-detect)

跟 [以前的版本](https://jiayu0x.com/2019/02/24/extract-compressed-files-by-static-analysis-in-watchdogsminer/) 一样，LSDMiner 的样本仍然是用 Go 编写，但是内部代码结构以及具体功能已经跟旧版本有很大差异。明显的差异至少有以下 3 点：
- 放弃了使用 Pastebin 作为恶意 Shell 脚本的下发通道，转而使用自己维护的 CC 服务器( `*.systemten.org` )来承载相关恶意活动；
- 集成了多个漏洞 Exp，增强传播能力，详见 Anomali 的 Blog；
<li>利用 DNS TXT 记录下发多种经过 AES 加密的数据，这些加密数据有以下几种：
<ul>
- 最新的恶意 Cron 任务用到的恶意 Shell 脚本下载 URL，可以写入失陷主机的 Cron 任务；
- 最新的恶意样本版本号，失陷主机上已有的恶意样本会对比自己的版本号以决定是否 Update；
- 最新的恶意 Shell 脚本；
- 一系列最新二进制样本的下载 URL。
其他恶意行为按照常规的逆向分析方法按部就班分析即可，而关于加密的 DNS TXT 数据的逆向与解密过程，Anomali 的 Blog 中描述一带而过，并没详述，按照他们 Blog 中简单的描述，并不足以解密这些数据。本文就以上述样本为例，解析一下如何通过逆向样本一步一步解密这些数据。



## 2. 恶意样本执行流程

恶意样本总体的执行流程分为 3 步：
1. 通过 DNS TXT 通道获取用来篡改失陷主机 Cron 任务的恶意 URL，被篡改后的 Cron 任务会定期访问恶意 URL 获取最新的恶意 Shell 脚本；
<li>扫描当前 B 段网络，存活的 IP 尝试利用 4 种方式入侵并植入，4 种方式有：
<ul>
1. SSH 爆破；
1. Redis 未授权访问；
1. Jenkins RCE 漏洞(CVE-2019-1003000)利用；
1. ActiveMQ RCE 漏洞(CVE-2016-3088)利用
</ul>
</li>
1. 持久驻留失陷主机、释放矿机程序挖矿。
在最后第 3 步，也会通过 DNS TXT 通道获取最新恶意 Shell 脚本以及二进制样本的下载 URL。本文重点分析 DNS TXT 通道数据的获取以及解密。

先看一下恶意样本通过 DNS TXT 通道获取最新的用来篡改失陷主机 Cron 任务的恶意 URL 的整体流程：

[![](https://p1.ssl.qhimg.com/t0199bd6bc19560f4bb.png)](https://p1.ssl.qhimg.com/t0199bd6bc19560f4bb.png)

可以看到样本首先从`cron.iap5u1rbety6vifaxsi9vovnc9jjay2l.com` 获取数据，然后用 AES-128bit 算法将其解密。再看一下从 `cron.iap5u1rbety6vifaxsi9vovnc9jjay2l.com` 获取的加密数据：

[![](https://p5.ssl.qhimg.com/t01f37621ba884fe28c.png)](https://p5.ssl.qhimg.com/t01f37621ba884fe28c.png)

DNS TXT 响应是一串字符，而且是经过 Base64 编码的字符串 **A7PZtADnYAEMEArGhmA9xQihPq9TRz4QigssjeOmUnQ** 。函数 **github_com_hippies_LSD_LSDC__AesCipher128_Decrypt()** 中的处理流程可以证实这一点：

[![](https://p1.ssl.qhimg.com/t01c8d6449234131fdc.png)](https://p1.ssl.qhimg.com/t01c8d6449234131fdc.png)

到这里可以看出，要用 Go 语言编程解密这些数据，需要 3 步走：
1. Base64 解码 DNS TXT 的响应字串，得到待解密的二进制数据；
1. 初始化 Go AES-128bit 解密句柄；
1. 解密 Base64 解码过的二进制数据。


## 3. Base64 解码

先用 Linux 自带的命令行工具 **base64** 尝试解码：

[![](https://p3.ssl.qhimg.com/t01f5a71963815547a0.png)](https://p3.ssl.qhimg.com/t01f5a71963815547a0.png)

有点蹊跷，不能用 base64 命令直接解码，看来用的并不是标准的 Base64 编码。这里先补充一下关于 Base64 编码的两点背景知识：
1. 参考: [RFC4648](https://tools.ietf.org/html/rfc4648) ，Base64 编码主要有两种：**标准编码(StdEncoding)** 和 **URL 安全的编码(URLEncoding)**。标准 Base64 编码的编码字符表是 **ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/** ，而 URLEncoding 的编码字符表则把 StdEncoding 编码字符表中的 **+** 替换为 **–**，把 **/** 替换为 **_** ，即 **ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_** ；
1. Base64 两种编码的默认填充字符都是 **=** ，但也可以选择不填充任何字符。
上述两个知识点，在 [Go 的 Base64 标准库文档](https://golang.org/pkg/encoding/base64/?m=all) 开头就有说明：

[![](https://p3.ssl.qhimg.com/t0111c0f0728a762d36.png)](https://p3.ssl.qhimg.com/t0111c0f0728a762d36.png)

两个知识点各自分为两种情况，这样组合起来就有 4 种细分的 Base64 Encoding：

[![](https://p1.ssl.qhimg.com/t012964db3cfe520697.png)](https://p1.ssl.qhimg.com/t012964db3cfe520697.png)

那 LSDMiner 样本中具体是用什么样的 Base64 解码呢？需要先看一下样本中 Base64 解码的 Encoding 句柄是如何生成的。在函数 **github_com_hippies_LSD_LSDC__AesCipher128_Decrypt()** 中，是先拿到 Base64 解码的 Encoding 句柄再进行解码：

[![](https://p5.ssl.qhimg.com/t017b5514e35863ed05.png)](https://p5.ssl.qhimg.com/t017b5514e35863ed05.png)

通过上面的 xrefs 信息，可知这个 **b64EncodingObj** 是在函数 **encoding_base64_init()** 中生成的。进入这个 init 函数，**b64EncodingObj** 生成过程如下：

[![](https://p1.ssl.qhimg.com/t01920c2ea1ed60c504.png)](https://p1.ssl.qhimg.com/t01920c2ea1ed60c504.png)

可以看到这样两点：
1. 调用 base64.NewEncoding() 函数时，传入的参数是 URLEncoding 的编码字符表，即样本中用的是 URLEncoding 形式的 Base64 编码；
1. 调用 base64.URLEncoding.WithPadding() 函数时传入的参数是 **-1** ，即 **base64.NoPadding** ，不带填充字符，即 **base64.RawURLEncoding**。
至此就可以解码 DNS TXT 响应的字符串了。测试代码与结果如下：

[![](https://p5.ssl.qhimg.com/t01ba448a6567c50303.png)](https://p5.ssl.qhimg.com/t01ba448a6567c50303.png)



## 4. AES 解密二进制数据

通过前面粗略的逆向分析，我们仅知道样本中用了 AES-128bit 算法来解密数据，但这些知识远不足以解密上面用 Base64 解码得到的二进制数据。AES 加密算法此处不详述，可以自行搜索相关资料，本文只关注如何用算法来解密数据。要想正确解密数据，还需要确定以下 AES 解密算法相关的几个要素：
- AES 密钥；
- AES 解密用到的 IV 向量；
- AES 解密算法的分组密码模式；
- AES 解密算法的 Padding 方式。
上面的逆向分析过程中，我们注意到样本中调用了函数 **crypto_cipher_NewCBCDecrypter()** ，可以确认样本中用到的分组密码模式是 **CBC**。

在分析确认其他几个要素之前，我们先捋一下两个关键函数的逻辑：初始化 AES 解密句柄的 **NewAesCipher128()** 和 执行 AES 解密操作的 **AesCipher128_Decrypt()**。

### <a class="reference-link" name="4.1%20NewAesCipher128"></a>4.1 NewAesCipher128

首先，样本调用该函数的时候传入一个参数，即待查询 DNS TXT 记录的域名字符串 `cron.iap5u1rbety6vifaxsi9vovnc9jjay2l.com`：

[![](https://p2.ssl.qhimg.com/t017e41c4aa797540e1.png)](https://p2.ssl.qhimg.com/t017e41c4aa797540e1.png)

在函数内部先初始化一个 **crypto/md5** 句柄（代码片段对照左边标准库函数 **crypto_md5_New()** 即可理解)：

[![](https://p1.ssl.qhimg.com/t0110130c1c190ce27d.png)](https://p1.ssl.qhimg.com/t0110130c1c190ce27d.png)

然后将传入的域名字符串由 string 类型转成字符切片并写入 MD5 digest 对象，再通过 **md5.digest.Sum()** 函数做一次 MD5 Hash 计算(注意 Sum 函数传入的参数为 **nil** )：

[![](https://p2.ssl.qhimg.com/t01a1a3d36311d783f9.png)](https://p2.ssl.qhimg.com/t01a1a3d36311d783f9.png)

再把这轮 MD5 计算的值通过 **hex.EncodeToString()** 转成 32-bytes 的字符串，即常规的字符串形式的 MD5 值。然后取出再取出这个 MD5 值的**前 16 字节**，保存到变量(**r1HashStr_16bytes**)中备用：

[![](https://p0.ssl.qhimg.com/t01e476c2ed74040c91.png)](https://p0.ssl.qhimg.com/t01e476c2ed74040c91.png)

接下来，样本又做了一次 MD5 计算，并且取出这一次 MD5 值的**后 16 字节**，保存到变量中备用(注意，这一次 MD5 计算之前没有调用 md5.dgest.Write() 来写入新字节，并且调用 md5.digest.Sum() 函数时依然传入参数 **nil** ):

[![](https://p1.ssl.qhimg.com/t01cd8cd3cbfb482e93.png)](https://p1.ssl.qhimg.com/t01cd8cd3cbfb482e93.png)

后面可以看到，第一次 MD5 计算后取出的 **前 16 字节** 数据，被作为 **AES 密钥**传入 **aes.NewCipher()** 函数来初始化 AES 解密句柄：

[![](https://p3.ssl.qhimg.com/t0127d72535e46643d6.png)](https://p3.ssl.qhimg.com/t0127d72535e46643d6.png)

而第二次 MD5 计算后取出的 **后 16 字节** 数据被保存起来，作为本函数返回值的一部分返回，接下来作为 **AES 的 IV 向量**传给后面函数 **AesCipher128_Decrypt()** 中调用的 **crypto_cipher_NewCBCDecrypter()** 函数。

### <a class="reference-link" name="4.2%20AES%20%E7%9A%84%20Padding%20%E6%96%B9%E5%BC%8F"></a>4.2 AES 的 Padding 方式

前面内容分析确认了 AES 的 Key、IV 以及分组密码模式，还需最后确认 AES 算法所用的 Padding 方式，即可正确解密数据。这一个点需要逆向分析函数 **AesCipher128_Decrypt()** 才能确认。

AES 加密算法用到的常见的 Padding 方式有以下几种(参考： [对称加密算法和分组密码的模式](https://www.jianshu.com/p/b63095c59361))：
- ANSI X.923：也叫 **ZeroPadding**，填充序列的最后一个字节填`paddingSize`，其它填0。
- ISO 10126：填充序列的最后一个字节填`paddingSize`， 其它填随机数。
- PKCS7：填充序列的每个字节都填`paddingSize` 。
LSDMiner 中用到的 Padding 方式就是简单的 ZeroPadding，通过函数 **AesCipher128_Decrypt()** 中解密操作后的 **byte.Trim()** 函数即可确认：

[![](https://p0.ssl.qhimg.com/t018b923b18d0ed6fdf.png)](https://p0.ssl.qhimg.com/t018b923b18d0ed6fdf.png)

### <a class="reference-link" name="4.3%20%E8%A1%A5%E5%85%85%E8%AF%B4%E6%98%8E%E2%80%94%E2%80%94%E5%85%B3%E4%BA%8E%E4%BA%8C%E8%BD%AE%20MD5%20%E5%80%BC%E8%AE%A1%E7%AE%97"></a>4.3 补充说明——关于二轮 MD5 值计算

上述分析过程中描述过，恶意样本为生成 AES 解密用到的 Key 和 IV 向量，对相应域名字符串连续做了 2 轮 MD5 Hash 计算，这一点 Anomali 的 Blog 中也提到了，只是他们没提到 Key 和 IV 具体的生成过程。

然而样本中连续两轮的 MD5 计算的值其实是相同的——这是 Go 语言特有的 MD5 计算方式，参考 [hash – Golang md5 Sum()函数](https://codeday.me/bug/20190214/636073.html) ，演示代码如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0124cf6cca12295a61.png)

这一点不知道是恶意软件作者的失误，还是有意为之。倒是容易给逆向分析造成困扰，因为乍一看“两轮 MD5 计算”，很可能直观认为应该得出两个不同的 MD5 值，并分别截取一段做 AES 解密的 Key 和 IV 向量，没想到两次 MD5 计算得出相同的值。



## 5. 完成解密

基于以上分析，就可以编写程序完成我们想要的解密工作了。完整的 Go 语言代码已上传到 Github：

[https://github.com/0xjiayu/LSDMiner_DNS_TXT_Decrypt](https://github.com/0xjiayu/LSDMiner_DNS_TXT_Decrypt)

运行结果如下：

[![](https://p3.ssl.qhimg.com/t018a594cec5c93f984.png)](https://p3.ssl.qhimg.com/t018a594cec5c93f984.png)

当前解密出来的 Cron URL 是 **`lsd.systemten.org`** ，在样本中如果整个 DNS TXT 数据通道操作过程有任何异常而无法解密出最新的 Cron URL，备用的默认值也是这个 **`lsd.systemten.org`** :

[![](https://p2.ssl.qhimg.com/t01292a0ef890ed206f.png)](https://p2.ssl.qhimg.com/t01292a0ef890ed206f.png)



## 6. 总结

文章开头的截图中已经显示过，如果样本用 **net.LookupTXT()** 函数检索 DNS TXT 记录失败，还会跳转到另外一个代码分支，去用 DoH(DNS over HTTPS) 向 CloudFlare 的 DoH 服务器请求相应的 DNS TXT 记录：

[![](https://p4.ssl.qhimg.com/t0179409c2e475573ef.png)](https://p4.ssl.qhimg.com/t0179409c2e475573ef.png)

[![](https://p3.ssl.qhimg.com/t01814f92e39daa49da.png)](https://p3.ssl.qhimg.com/t01814f92e39daa49da.png)

我们用命令行工具测试一下，可以看到这种方式也有效：

[![](https://p4.ssl.qhimg.com/t0190241a9fdaadb4ad.png)](https://p4.ssl.qhimg.com/t0190241a9fdaadb4ad.png)

利用 DNS TXT 记录和 DoH 下发恶意数据来辅助恶意样本的运行，可以进一步提升整个 Botnet 基础设施的健壮性和运营的灵活性，鉴于这个 Botnet 存活已久并不断更新，应该引起业界的持续关注。

前文说过，恶意样本中利用 DNS TXT 通道传输的数据还有其他几种，方式都是一样：检索 DNS TXT 数据，用 base64.RawURLEncoding 解码得到二进制数据；然后对域名进行 MD5 计算得出 AES 解密用到的 Key 和 IV，然后用 CBC 模式、ZeroPadding 的 AES-128bit 算法对 Base64 解码后的二进制数据进行解密。对应的域名还有以下几个，均可以用以上 Go 程序来解密：

```
"update.iap5u1rbety6vifaxsi9vovnc9jjay2l.com"
"shell.iap5u1rbety6vifaxsi9vovnc9jjay2l.com"
"1x32.iap5u1rbety6vifaxsi9vovnc9jjay2l.com"
"2x32.iap5u1rbety6vifaxsi9vovnc9jjay2l.com"
"3x32.iap5u1rbety6vifaxsi9vovnc9jjay2l.com"
"1x64.iap5u1rbety6vifaxsi9vovnc9jjay2l.com"
"2x64.iap5u1rbety6vifaxsi9vovnc9jjay2l.com"
"3x64.iap5u1rbety6vifaxsi9vovnc9jjay2l.com"
```

另外，LSDMiner 涉及的二进制恶意样本，都用变形 UPX 加了壳，而且壳的特征很不明显，难以用固定的特征直接检测加壳的样本。并且，相关加壳二进制样本的 UPX 壳幻数(Magic Number)还经常变化，比如本文分析的 MD5 为 **114d76b774185b826830cb6b015cb56f** 的 UPX 壳幻数为 **0x2124922A**；最新的 x86_64 架构的样本(MD5: **78e3582c42824f17aba17feefb87ea5f**) 的 UPX 壳幻数则变成了**0x215E77F2** 。
