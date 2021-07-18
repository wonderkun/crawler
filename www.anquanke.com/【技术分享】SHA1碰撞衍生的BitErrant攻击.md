
# 【技术分享】SHA1碰撞衍生的BitErrant攻击


                                阅读量   
                                **90790**
                            
                        |
                        
                                                                                                                                    ![](./img/85697/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://biterrant.io/](https://biterrant.io/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85697/t017988afd02cafa0e8.jpg)](./img/85697/t017988afd02cafa0e8.jpg)

****

翻译：[knight](http://bobao.360.cn/member/contribute?uid=162900179)

预估稿费：120RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**前言**

BitErrant攻击是一个非常有趣的小漏洞，当SHA1碰撞变成现实时，BitTorrent协议可能就会出错。

当发生SHA1碰撞时可能会导致大量下载的文件被其他文件所替代，还可能会损坏文件或触发后门漏洞。

当受害者使用BitTorrent协议下载可执行文件时，攻击者可以通过更改组块来更改可执行文件的执行路径。

谢谢Google和CWI的朋友，帮助我们实现SHA1碰撞和[SHAttered](http://shattered.io/)攻击！

<br>

**概念证明**

这里有两个具有不同的功能的EXE文件（恶意文件有一个meterpreter，它可以侦听所有的接口），这两个EXE会产生相同的.torrent文件。

文件下载： [biterrant_poc.zip](https://biterrant.io/files/biterrant_poc.zip)

密码：biterrant.io

SHA1：eed49a31e0a605464b41df46fbca189dcc620fc5（你知道，因为什么导致了出错？）

此外，这里有一个关于如何生成这样的可执行文件的复杂（LOL）框架。

更新（2017.03.06）

当前统计信息：

[virustotal上的正常文件](https://virustotal.com/en/file/aab71ef7bf13e4fe8613d4f1f9ae136cd7f03474c0e576f0de6f9fc4c15edd97/analysis/1488732404/)

[virustotal上的恶意文件](https://virustotal.com/en/file/0624ed0bad3edf8308004b323d6f3cfd70751395dc93bd1108f7a6df87223102/analysis/1488732438/)

###VirusTotal是一个提供免费的可疑文件分析服务的网站。

BitTorrent的工作原理（简单的解释一下）

[![](./img/85697/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018c47c0f42b668fc3.jpg)

BitTorrent分发文件的第一步是从原始文件（DATA）生成“.torrent”形式的文件。 这是通过将文件切成固定大小的数据块，然后计算每个数据块上的SHA1哈希值。然后将哈希字节连接在一起，并存储到torrent文件中的“pieces”字典键下。

[![](./img/85697/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01064b8832be90d1cb.jpg)

当有人尝试使用BitTorrent下载DATA文件时，BitTorrent会先下载并解析“DATA.torrent”文件。 基于存储在DATA.torrent文件中的信息，客户端会去搜索与它相对应的数据进行匹配，然后再下载原始文件（DATA）的数据块。为了确保搜索到的对应模块不会发送恶意数据，客户端会针对存储在DATA.torrent文件中的散列数据，进行每个下载数据块的验证。 如果torrent文件中的哈希数据与下载的数据块的SHA1哈希不匹配话，不匹配的数据就会被丢弃。

<br>

**恶意的意图**

[![](./img/85697/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012cf360d782d922cd.jpg)

攻击者可以创建一个可执行文件，该文件在执行时看起来并无异常，但会根据SHATTER区域内的数据更改其执行路径。 当然，当使用AntiVirus软件检查文件也不会检测出任何异常，因为恶意代码被隐藏在加密的blob中，并永远不会被执行。 对吗？

[![](./img/85697/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ba184667d84f35d2.jpg)

好吧，不完全是。 如果攻击者有两个blob的数据块，并且具有匹配的SHA1哈希值。在考虑到一些约束情况下，生成两个包含不同数据的可执行文件，并且产生相同的.torrent文件是有可能的！

[![](./img/85697/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b0820fd395d4c983.jpg)

如果满足以上提及的限制，那么两个可执行文件就会产生一个可互换的数据块。 攻击者可以替换这个数据块来触发代码中的恶意代码。

[![](./img/85697/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c6be01391bce1b62.jpg)

关于如何通过BitTorrent协议检索到哪个数据块会执行（或不执行）shellcode的示例。

原理是当使用不正确的SHATTER数据时，解密会产生垃圾数据。 例如，[shatter-2.pdf](http://shattered.io/static/shattered-2.pdf)碰撞数据用于加密，[shatter-1.pdf](http://shattered.io/static/shattered-1.pdf)数据用于分发。 在下载期间，攻击者开始传播包含[shatter-2.pdf](http://shattered.io/static/shattered-2.pdf)数据的文件，这样就能够有效地替换一个数据块，同样也会触发客户端中的shellcode的解密和执行，客户端就会下载攻击者所指定的数据块。

<br>

**常见问题解答**

这个问题严重吗？

至少现在还不是很严重。当该漏洞被普遍利用时，我会重新评估这一声明。

我们应该如何保护自己？

经常核对MD5 SHA1 SHA256哈希MD4的下载文件。祝你找到的BT网站，会发布这样的哈希值：）

有一个选项：会生成一个torrent形式的文件，该文件包含完整数据文件的MD5哈希值。

大多数时候该选项不会被使用，并且不确定所有torrent客户端会使用它。

<br>

**致谢**

Hugo Maglhaes，他正在不厌其烦地看着代码。 还指出了错误。

Kamil Leoniak，他不仅在一句话中提到BitTorrent和shattered.io，还想出了整个攻击。

Nickol Martin，他希望保持匿名，因为她不喜欢她花5分钟设计的HTML的外观。 大概是她设计的标志太特别了。
