> 原文链接: https://www.anquanke.com//post/id/236131 


# 针对DNS转发设备的缓存投毒攻击


                                阅读量   
                                **111716**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Xiaofeng Zheng, Chaoyi Lu, Jian Peng, Qiushi Yang, Dongjie Zhou, Baojun Liu, Keyu Man, Shuang Hao, Haixin Duan, Zhiyun Qian，文章来源：usenix.org
                                <br>原文地址：[https://www.usenix.org/system/files/sec20-zheng.pdf﻿](https://www.usenix.org/system/files/sec20-zheng.pdf%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01e291b119cf5b1863.jpg)](https://p1.ssl.qhimg.com/t01e291b119cf5b1863.jpg)



## 1 前言

前些时间刚好看到一些缓存投毒相关的知识，搜了些资料，发现了安全顶会USENIX Security 2020上收录了一篇关于DNS缓存投毒的文章：Poison Over Troubled Forwarders: A Cache Poisoning Attack Targeting DNS Forwarding Devices。文中介绍了一种新型的针对DNS Forwarder也就是DNS Forwarder的缓存投毒攻击。通过这种攻击方式，攻击者可以向DNS Forwarder中注入任意的受害domain，将用户指引到恶意站点，并且可以规避目前的缓存投毒防御措施。该项研究的初期成果就曾在GeekPwn 2018上现场展示过，通过路由器上的缓存投毒，劫持了赛场上的无线路由器。



## 2 背景知识

首先稍微介绍下背景知识。

### <a class="reference-link" name="2.1%20DNS%E8%A7%A3%E6%9E%90%E4%BC%A0%E7%BB%9F%E6%9E%B6%E6%9E%84"></a>2.1 DNS解析传统架构

传统的DNS解析主要涉及Stub Resolver（存根解析器）、Recursive Resolver（递归解析器）和Authoritative Resolver（权威域名解析器）。

权威域名解析器能够从自己的数据满足查询，而不需要引用其他来源，即能够给出DNS查询请求的权威应答，递归解析器则是通过询问其他域名服务器获取答案，递归解析器最后能够权威域名解析器得到查询响应。

根据DNS协议的初始标准，当域名需要解析时，DNS客户端向递归解析器发送查询请求，递归解析器会从权威域名解析获取答案，然后将结果返回给客户端。

[![](https://p0.ssl.qhimg.com/t01fd1fd54d9df4dbf9.png)](https://p0.ssl.qhimg.com/t01fd1fd54d9df4dbf9.png)

### <a class="reference-link" name="2.2%20IP%E6%95%B0%E6%8D%AE%E5%8C%85%E5%88%86%E7%89%87"></a>2.2 IP数据包分片

IP（Internet Protocal）是TCP/IP协议族中的核心协议，所有TCP、UDP和ICMP等数据报都是通过IP数据报进行传输。互联网协议允许IP数据包分片，当数据包比链路最大传输单元（MTU）大的时候，就会被分解为很多的小分片，以便大数据包能够在链路上传输。

[![](https://p5.ssl.qhimg.com/t01f517e982d2a09926.png)](https://p5.ssl.qhimg.com/t01f517e982d2a09926.png)

被分片的IP数据包是通过IP首部的一些字段进行重新组装的。这些字段有4个，首先是Identification位，简称为IPID，是IP数据包的标识字段，这些标识字段都是一个单一值，这个值在分片的时候被复制到每一个分片中。 DF(Don’t Fragment)是不分片位，置为1就表示不会对数据包进行分片操作。MF(More Fragment)是更多的分片位，除了最后一片以外，其他每个组成数据包的分片都要把这个位置为1。Fragment Offset是当前数据包分片距离原始数据包开始处的位置，偏移的字节数是字节乘以8。其中最重要的是IPID，后面论文中会用到这个标志位信息。



## 3 DNS缓存投毒历史

此前的DNS缓存攻击主要是针对递归解析器的。主要有两种方式：

### <a class="reference-link" name="3.1%20%E4%BC%AA%E9%80%A0%E6%94%BB%E5%87%BB"></a>3.1 伪造攻击

伪造攻击（Forging Attacks）的目的是制造一个恶意DNS响应，并欺骗递归解析器去接受它。当DNS响应数据包中的一些字段和DNS请求数据包中的字段相匹配时，DNS响应数据包就会被解析器所接受，这些字段是：

> <p>Question Section 查询问题<br>
DNS transaction ID 会话标识<br>
source/destination addresses 源地址/目标地址<br>
port numbers 端口号</p>

如果攻击者在经过身份验证的响应到达之前用正确的metadata伪造DNS响应，那么解析器就会接受该伪造的响应，攻击成功。攻击者要在真正的响应包返回之前，迅速发出多个伪造的响应包，以便让递归解析器接受其中某一个响应包，如果成功，那真正的相应包就会被丢弃。

通过伪造DNS响应包来攻击的最知名的案例是2008年的Kaminsky攻击，它影响了几乎所有的DNS软件和设备。

[![](https://p3.ssl.qhimg.com/t017036da8e8fcf5538.png)](https://p3.ssl.qhimg.com/t017036da8e8fcf5538.png)

前面说到DNS解析器会根据查询数据包中的几个字段对响应包进行匹配，会话标识对不上的、端口对不上的都会被DNS解析器抛弃，所以攻击主要存在几个难点：

> <p>1 . 首先，攻击者需要知道UDP报文中的源端口号才能构造响应包中的端口号。虽然攻击者不能窃听，但是在Kaminsky攻击之前，DNS报文中的大多数源端口都不是采用随机化的方式分配的，通常一些DNS解析器会直接采用53作为源端口号，或是操作系统中的一个固定值。<br>
2 . 除了端口号之外，DNS响应报文中的其他字段也需要和DNS请求包能够对应，否则就会被DNS解析器抛弃。</p>

针对这种攻击目前的缓解措施主要有：

> <p>1 . ID/端口随机化，使用随机短暂的端口号和会话标识。<br>
2 . 0x20 encoding，即随机化大小写验证技术，该技术会匹配请求包和响应包的大小写，如果大小写不匹配就会丢弃响应包。比如对于长度为8个字符串的域名，那么就会产生2^8个不同的字符串，但是这种方式也有一定的局限性，因为一些授权DNS服务器并不支持大小写混合应答。</p>

### <a class="reference-link" name="3.2%20%E5%88%86%E7%89%87%E6%95%B4%E7%90%86%E6%94%BB%E5%87%BB"></a>3.2 分片整理攻击

最近的研究又发现了一种基于IP分片整理（Defragmentation Attacks）的新型DNS缓存投毒攻击方法。这种攻击主要利用了这样一个事实，即被分片的DNS响应包中的第二个分片段并不包含DNS或UDP报文中的报头（header）或是问题部分（question section），所以这种攻击方式可以避开针对伪造攻击的防御措施，如ID/端口随机化措施。

简要的攻击流程如下图所示：

[![](https://p0.ssl.qhimg.com/t01e3fd3b9ee54bca1e.png)](https://p0.ssl.qhimg.com/t01e3fd3b9ee54bca1e.png)

首先，攻击者构造虚假的第2个分片(2nd fragment)，将这个不完整的第2个分片数据包发送给递归解析器，递归解析器缓存该记录。

然后攻击者发起关于受害domain的DNS查询请求，递归解析器的记录中没有相关记录，所以会再去询问权威解析器。

从权威解析器返回的数据包因为某些不可抗力因素被分片转发给递归解析器。然后在递归解析器这里，从权威解析器发出的第一个合法的分片数据包和之前缓存在递归解析器的第2个攻击者伪造的分片数据包重新组装，最后形成一个能被递归解析器接受的“合法”响应包。并且该响应被递归解析器缓存下来。

上述攻击的关键步骤就是在第2步中的权威解析器必须以分片的方式向递归解析器发送响应包。主要有两种方式：

> <p>1 .降低PMTU数值<br>
2 . 发送DNSSEC查询，用DNSSEC记录填充DNS响应数据包，使它们达到MTU的限制，从而迫使数据包通过分片的方式转发。DNSSEC（Domain Name System Security Extensions）是DNS安全扩展机制，是由IETF提供的一系列DNS安全认证机制，它提供一种来源鉴定和数据完整性扩展。DNSSEC依靠数字签名来保证DNS应答报文的真实性和完整性。DNSSEC服务器对DNS解析器的应答，采用DNSSEC的签名方式，然后DNS解析器使用签名来验证DNS响应，确保记录未被篡改。</p>

这种攻击方式也存在一些限制，PMTU-based碎片整理攻击需要攻击者先伪造一个发送给权威域名解析器的ICMP包，来欺骗权威域名解析器去降低PMTU数值。但是作者发现这在大多数情况下不太适用。如下图所示，对于Alexa网站上排名前100K的权威域名服务器，在构造这样的ICMP数据包之后，只有0.7%的权威域名服务器将它们的PMTU值降低到528bytes之下。**由于DNS响应数据包通常小于512字节，因此它们不太可能被强制分片**。



## 4 DNS Forwarder

传统上，DNS解析过程涉及DNS客户端（或存根解析器）、递归解析器和权威服务器。当一个域名在客户端找不到记录，那就需要向递归解析器发起查询请求，递归解析器就会向权威域名解析器咨询答案。相较于这个最简单的模型，DNS解析设施变得越来越复杂了，通常涉及多层服务器，其中一种新的DNS基础设被就是DNS Forwarder，它们位于存根解析器和递归解析器之间，通常充当DNS客户端的入口服务器：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019b6eaf54a03b35af.png)

当DNS Forwarder接收到查询请求时，它不递归地执行解析，而只是将查询转发到上游的递归解析器。比如家庭路由器就具备DNS转发的功能。<br>
相比于Recursive Resolver，DNS Forwarder的运行机制就没那么复杂，它无需对DNS客户端的查询请求进行递归解析，只是起转发的作用；而且其在安全性上依赖于上游的递归解析器，不会对response进行检查，这也是DNS Forwarder的一个关键弱点，这个特性使得针对DNS Forwarder的缓存投毒攻击成为可能。



## 5 针对DNS Forwarder的分片整理攻击

前面介绍的分片整理攻击是针对DNS递归解析器的，因为DNS Forwarder中不会对数据包进行安全性校验的特性，作者在论文中提出了一种针对DNS Forwarder的分片整理攻击方法。

### <a class="reference-link" name="5.1%20%E6%94%BB%E5%87%BB%E6%A8%A1%E5%9E%8B%E6%A6%82%E8%BF%B0"></a>5.1 攻击模型概述

**攻击模型** 研究表明目前有大量运行在住宅网络设备上的DNS Forwarder，比如家庭路由器。 因此，在威胁模型中，作者假设攻击者位于与DNS

相同的局域网中，并且可以发出DNS查询。这种攻击场景可以出现在公开的Wi-Fi网络中，比如在咖啡馆或是机场这些公开场所中。

在攻击之前，需要先回答一个问题：我们能够可靠和确定地使响应数据包分片吗？

事实证明， 如果查询被发送到攻击者控制下的权威域名服务器，然后使被控制的权威域名服务器发送超大的响应包，就可以使响应数据包分片。乍一看，这是毫无意义的，因为控制了权威域名服务器就意味着权威域名服务器上托管的域也已经属于攻击者了。攻击者向被自己控制的域进行缓存投毒是毫无意义的。但是这篇文章的insight是，DNS Forwarder是不会进行响应包的安全校验的，它对响应包的安全性判断完全依赖于它上游的递归解析器。

**攻击流程** 下图是论文中涉及的针对DNS Forwarder的缓存投毒攻击流程图。

[![](https://p2.ssl.qhimg.com/t010581e92b4b0d5cf3.png)](https://p2.ssl.qhimg.com/t010581e92b4b0d5cf3.png)

第一步，首先需要探测IPID（IP标识，是IP数据包头中的一个16位的字段，用于确定分片属于哪个数据报），IPID如何预测这在后面会提到，也是成功攻击的关键之一。

然后，构造响应数据包的第2个分片，包含一条伪造的A记录，将IP地址指向攻击者控制的恶意IP地址，该不完整的数据包在DNS Forwarder这里被缓存。

接着，攻击者发起DNS查询请求，查询a.attaker.com的IP地址，DNS Forwarder将该查询转发给递归解析器，递归解析器本地缓存中不存在对该域名的记录，所以向权威域名解析器发起查询请求。

最后，权威域名解析器返回响应数据包给递归解析器，因为权威域名解析器是被攻击者控制的，所以在生成响应包的时候，向里面填入很多条CNAME记录，将响应数据包填充得很大（3a.），该数据包被返回给递归解析器，该响应数据包是能够通过递归解析器的安全性校验的，递归解析器再将该response响应转发给DNS Forwarder，因为数据包很大，所以会被分片转发（3b.），当第一片合法的分片数据包到达DNS Forwarder的时候，会和之前构造的2nd分片（缓存在DNS Forwarder中）重新组合成完成的数据包，这里能够重新组装是因为2nd分片中的IPID是预测过的，能和第一个合法的分片匹配上。因为DNS Forwarder不会对数据包进行检查，所以会直接将这个结果转发给DNS客户端（3c.）。这就是完整的攻击流程。

可以看到和DNS伪造攻击不同，分片整理攻击不再需要对DNS会话标识和端口号等metadata信息进行构造了，因为在2nd分片中并不包含这些信息了，这些信息仅存在于第一个分片包中 。

### <a class="reference-link" name="5.2%20DNS%E5%93%8D%E5%BA%94%E5%88%86%E7%89%87"></a>5.2 DNS响应分片

上面的攻击流程中已经知道，使递归解析器转发给DNS Forwarder的响应数据包成功分片是成功攻击的关键点之一。此前已经介绍过了，之前的研究主要有两种方式来迫使DNS响应包分片：一、通过降低PMTU值；二、用DNSSEC来填充响应包。但是这两种方式都不太可取。

本文采取的方案和用DNSSEC填充是类似的，利用CNAME记录来填充DNS响应数据包。

[![](https://p2.ssl.qhimg.com/t01befa0e8e6edc97ca.png)](https://p2.ssl.qhimg.com/t01befa0e8e6edc97ca.png)

攻击者控制的权威域名服务器可以有意地创建大于以太网MTU值的超大DNS响应数据包，那么递归解析器收到相应包再将其转发给DNS Forwarder的时候，会对其进行分片操作。

具体的方法就是构造CNAME记录链（CNAME records chain），最后跟一个最终的A记录。

[![](https://p1.ssl.qhimg.com/t0126bd4a449919e758.png)](https://p1.ssl.qhimg.com/t0126bd4a449919e758.png)

在伪造的2nd分片中，将最后的一条CNAME记录指向victim.com，然后最后跟一条关于victim.com的A记录，指向恶意IP地址a.t.k.r。

对于上游的递归解析器来说，它们看到的是来自权威域名解析器的超大dns响应包，经过校验并不违反bailiwick规则，所以递归解析器就将这个超大响应包以分片的方式转发给DNS Forwarder了。

使用这种超大DNS数据包响应需要攻击场景中的所有DNS服务器都支持**DNS扩展名机制（Extension Mechanisms for DNS(EDNS(0))）**。EDNS被提出来的理由之一是，当初DNS协议中设计的用UDP包传输时，将包的大小限制在512字节，但是现在很多的主机已经具备重组大数据包的能力，所以需要一种机制能够允许DNS请求方通知DNS服务器让其返回大数据包。在DNS数据包头部中添加了一个OPT字段来标记该数据包是否携带EDNS选项。

### <a class="reference-link" name="5.3%20%E6%9E%84%E9%80%A0%E6%81%B6%E6%84%8F%E5%88%86%E7%89%87"></a>5.3 构造恶意分片

如果DNS数据包被分片，则只有第一个片段将具有UDP报头和DNS报头。因此，要构造第2个恶意的分片，攻击者就不需要再预测DNS和UDP报头中的端口号和会话标识（Transaction ID）等metadata信息了。然而，为了成功地碎片整理，攻击者还需要构造IP header中的Identification字段信息（后面简称为IPID），这样才能够在第1个合法的数据包分片到达DNS Forwarder的时候和构造的2nd分片成功组合，因为IP数据包分片要有相同的IPID才能够重新组装。因此，攻击者还需要预测上游的递归解析器的IPID分配。

目前一共有3种IPID分配算法：
<li>
**全局IPID计数器**<br>
全局IPID计数器就是为每个数据包增加一个计数单位1，这是非常容易预测的。</li>
<li>
**基于哈希的IPID计数器**<br>
想象现在有个IPID计数器数组，基于哈希的IPID计数器首先利用数据包的源ip地址和目的ip地址映射到IPID计数器数组中的某个counter，比如为A，然后将两次使用同一个counter A的系统时间间隔记为X，然后在1到X之间选一个随机数R加到A上，IPID就变为了A+R。只要发送的两次数据包即Current IPID和Predicted IPID时间够近，那么成功预测的概率很大，而且因为DNS Forwarder一次可以缓存64个分片，所以攻击者可以在很短的时间内发送多个构造的分片来提高成功率。</li>
<li>
**随机IPID分配**<br>
随机性变大，比较难预测。</li>
### <a class="reference-link" name="5.4%20%E6%94%BB%E5%87%BB%E6%9D%A1%E4%BB%B6%E6%80%BB%E7%BB%93"></a>5.4 攻击条件总结

根据前文中的攻击模型可知，成功的攻击条件有：

**EDNS(0) support**

EDNS(0)机制允许通过UDP传输比较大的DNS数据包，从而允许传输大于512字节的DNS消息来迫使数据包通过分片的方式从递归解析器传送到DNS Forwarder。

**No truncation DNS response**

尽管一些DNS Forwarder支持EDNS(0)机制，但是部分Forwarder还会截断大DNS响应数据包，即使一些响应数据包没有达到以太网MTU的最大值。在这种情况下，被截断的DNS响应数据包是不会被分片的，那么碎片整理攻击自然就会失败了。这里要明确的是，IP数据包截断（truncation）和分片（fragmentation）是不同的操作，如果数据包被截断之后，会被标记为是一个已截断的数据包，多余的部分会被丢弃，然后再将其转发到目的地。

**No verification of DNS response**

在DNS Forwarder中不能存在对DNS响应的验证，攻击原理的核心就是DNS Forwarder对数据包的验证完全来自上游的Recursive Resolver。

**DNS caching by record**

在DNS Forwarder中，有两种方式来缓存DNS响应结果，一种是将DNS响应作为整体缓存下来，即整个DNS响应作为一条缓存记录；另一种方式是以记录的方式缓存结果。举个例子，如下图的DNS响应：

[![](https://p0.ssl.qhimg.com/t0100b36f07678ac26c.png)](https://p0.ssl.qhimg.com/t0100b36f07678ac26c.png)

如果将DNS响应作为整体缓存下来，那么最后只有一条关于a.attacker.com的记录，对于我们的目标victim.com则完全不会被命中。反之，如果是以record的形式被缓存，那么当用户查询victim.com的时候，就会命中DNS Forwarder的缓存。



## 6 对问题的反思

那纠其原因，是什么导致的DNS Forwarder中的弱点呢？实际上，工业界并没有对DNS Forwarder应该在DNS生态系统中发挥的作用达成一致的意见。DNS Forwarder可以充当透明的DNS代理工具，也可以发挥一些递归解析器所具备的功能。但是，供应商并没有对DNS Forwarder的一些功能实现达成一致，比如DNS Forwarder是否应该具备缓存功能，是否应该对分片的数据包进行处理，以及是否能够自己发起请求来检查请求，比如说可以通过这种方式来验证CNAME链的合法性。

### <a class="reference-link" name="6.1%20DNS%20Forwarder%E8%A7%84%E8%8C%83"></a>6.1 DNS Forwarder规范

在查阅了DNS RFC标准文档之后，作者发现了不同的供应商对于DNS Forwarder有多种不同的功能实现可能是由于规范中模糊不清的定义导致的。在最开始的DNS标准文档（RFC 1034）中，是不存在DNS Forwarder的，但随着DNS Forwarder越来越流行，目前依旧缺少对于DNS Forwarder的清晰明确的规范。

查阅RFC文档，作者发现，甚至连标准文档都对DNS Forwarder有不同的定义，他们从7条RFC标准中找到了对DNS Forwarder不同的定义。

### <a class="reference-link" name="6.2%20%E7%BC%93%E8%A7%A3%E6%8E%AA%E6%96%BD"></a>6.2 缓解措施

在前面介绍攻击原理的时候已经介绍过攻击的4个先决条件了，所以可以认为只要破坏其中的任意一个条件就可以组织攻击的产生，但是事实上，阻止DNS Forwarder进行缓存或是禁止ENDS(0)机制都是不可行的，因为这些缓解措施会损害DNS Forwarder中的一些重要的新特性新功能。

所以防御措施只能从另外两个先决条件或是攻击准备条件上入手，比如预测IPID。



## 7 小结

该研究团队在一些家用路由器和一些路由软件上进行测试，证实了DNS forwarder上确实存在这样的缺陷。

该研究团队后来又对DNS缓存投毒进行更加深入地挖掘，紧随其后一篇发在CCS2020的文章**DNS Cache Poisoning Attack Reloaded: Revolutions with Side Channels**中又提出了一种侧信道攻击方法，能够对随机化的source port进行derandomize，从而成功预测分片，也是很值得一读的文章。
