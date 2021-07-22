> 原文链接: https://www.anquanke.com//post/id/102948 


# 我们来谈一谈IDS签名


                                阅读量   
                                **138384**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.ptsecurity.com
                                <br>原文地址：[http://blog.ptsecurity.com/2018/03/we-need-to-talk-about-ids-signature.html](http://blog.ptsecurity.com/2018/03/we-need-to-talk-about-ids-signature.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01840ee263510914c9.jpg)](https://p4.ssl.qhimg.com/t01840ee263510914c9.jpg)



## 一、前言

Snort和Suricata入侵检测系统在网络安全领域一直为人所熟知。WAF和IDS是两类安全系统，用来分析网络流量，解析上层协议，从而标记出恶意流量、攻击行为等。不同的是，WAF能够帮助服务器检测并避免仅针对他们的攻击，而IDS则是可以检测出所有网络流量中的恶意攻击（但仅限于检测）。<br>
许多公司安装IDS来监控内网中的流量。DPI机制（Deep Packet Inspection：深度包检测，一种基于应用层的流量检测和控制技术）可以让他们收集到IP，HTTP，DCE/RPC或者其他层的流量数据包，并识别出其中是否有利用漏洞或是其他恶意攻击行为的流量。<br>
这两种系统的核心都是用于检测已知攻击的签名集，这些签名集是由全球的网络安全专家以及安全公司共同开发维护。<br>
我们所在的团队attackdetection也开发过一些检测网络攻击以及恶意行为的签名。而接下来你在这篇文章中将看到我们发现的一种可以破坏Suricata IDS系统，并且能够隐藏攻击痕迹的方法。



## 二、IDS工作原理剖析

在深入研究IDS绕过技术的细节及其应用的阶段之前，我们先来重新阐述一下IDS背后的原理概念。

[![](https://p4.ssl.qhimg.com/t011eb1939ed588e0f0.png)](https://p4.ssl.qhimg.com/t011eb1939ed588e0f0.png)<br>
首先进来的流量被分为TCP流，UDP流或者其他流，然后解析器将其标记并分解为高层协议及其相关字段，并根据需要进行标准化处理。之后这些经过解码，解压，标准化后的协议字段会与检测网络流量中是否含有恶意攻击流量的签名集进行比对。<br>
顺便补充一点，签名集是众多安全研究人员与安全公司共同努力维护的产物。像比较有名的安全公司Cisco Talos以及Emerging Threats都参与其中。目前开放的规则集包含超过20000个签名。



## 三、常见的IDS绕过方法

IDS本身的缺陷以及一些软件使用错误有时就会导致其无法在流量中准确检测到攻击行为。下面是一些在流量解析阶段常见的绕过方法:

> <ul>
- 数据包的非标准分段（把请求分开放在不同的包文中），包括在IP，TCP，和 DCERPC层。IDS有时无法正确处理。
- 具有边界值或无效的TTL/MTU的数据包有时会被IDS不正确地处理。
- IDS系统不会像服务器或客户端那样正确处理TCP模糊重叠分片（TCP SYN序列号）。
- 例如，将具有无效校验和的TCP FIN虚拟数据包（所谓的TCP un-sync）解释为会话结束，而不是将其忽略。
- 有时IDS和客户端之间TCP会话的不同超时时间也可用作为隐藏攻击的工具。
</ul>

至于协议解析和字段规范化阶段，许多WAF绕过技术可以应用于IDS。下面介绍其中的一部分:

> <ul>
- HTTP双重编码。
- 经过Gzip压缩的HTTP数据包如果没有相应的Content-Encoding头，可能在标准化阶段保持未压缩状态;这种技术有时可以在恶意流量中检测到。
- 使用一些罕见编码（如POP3/IMAP的Quoted-Printable）也可能导致某些签名无效。
</ul>

并且不要忘记每一个IDS系统供应商有时都会被报出特定的BUG包括在其中使用的一些第三方库有时也会出现一些漏洞，这些都会在各大公共漏洞平台中找到。<br>
其中一个可以在特定条件下触发使得签名检测无效化的bug是由我们的团队attackdetection在Suricata系统中找到的；这个漏洞可以被利用造成像BadTunnel一样的攻击。<br>
在攻击过程中，受害者打开一个由攻击者生成的HTML页面，在双方之间建立一个UDP隧道，连接到攻击者服务器的137端口上。一旦建立了隧道，攻击者就可以通过向NBNS请求发送假响应来伪装成受害者。尽管有三个数据包发送到攻击者的服务器，但只需响应其中一个数据包即可建立隧道。<br>
产生这个问题的原因是，对来自客户端的第一个UDP数据包的响应是一个ICMP数据包，例如ICMP Destination Unreachable（端口不可达），IDS不够精确的算法将使得该数据流仅通过ICMP签名进行验证。任何进一步的攻击，包括身份伪造等，都未能被IDS检测出来，因为它们是在UDP隧道之上传输的。无论是否有此漏洞的标识、签名，都会导致IDS安全功能的丧失。

[![](https://p1.ssl.qhimg.com/t01be44176100a74f99.png)](https://p1.ssl.qhimg.com/t01be44176100a74f99.png)<br>
上述绕过技术都是众所周知的，并且在现代并长期开发维护的IDS系统中已被封禁、淘汰。而那些特定的BUG和漏洞仅适用于未打补丁的旧版本。<br>
因为我们的团队致力于网络安全以及网络攻击研究，而且也亲手开发，测试签名，所以我们一直在关注绕过签名以及签名本身相关缺陷的技术。



## 四、利用签名绕过签名检测

等一下，签名怎么会成为问题呢？<br>
研究人员对于突然出现的网络攻击威胁，首先会对其分析，得到如何检测这一攻击的规则。抽取其中的特征，并将结果转化为一个或多个签名并用IDS能够理解的语言编写出来。由于系统能力有限有时也因为研究人员的失误，一些利用漏洞的流量仍然无法检测出来。<br>
在协议族及信息格式不变，恶意软件发出的流量不变且针对他们的签名正常工作的情况下，如果协议及其可变性越复杂，攻击者就越容易在不改变恶意功能的情况下更改漏洞利用形式从而绕过签名检测。<br>
尽管您可以从不同的供应商那里找到许多检测最危险以及最受关注的一些漏洞的签名，但其他的签名有时可以通过简单的方法来绕过。以下是HTTP常见签名错误的示例：有时，只需更改HTTP GET参数的顺序即可绕过签名检查。<br>[![](https://p4.ssl.qhimg.com/t01680f35c1f2371c87.png)](https://p4.ssl.qhimg.com/t01680f35c1f2371c87.png)<br>
而且您可能认为在签名中检测具有固定顺序参数的子字符串是很常见的，例如“？action = checkPort”或“action = checkPort＆port =”。所需要的只是仔细比对签名规则，检查它是否包含这样的硬编码。<br>
其他一些同样复杂的协议、格式像DNS，HTML和DCERPC，它们都具有极高的可变性。因此，为了覆盖所有攻击变体的特征，不仅要开发高质量还要可以快速检测的签名。所以开发人员必须拥有广泛的技能以及拥有网络协议方面丰富的知识。<br>
IDS签名的不足之处已经是老生常谈了，您可以在很多报告中找到关于它的其他看法：[1](https://www.google.com/url?sa=t&amp;rct=j&amp;q=&amp;esrc=s&amp;source=web&amp;cd=3&amp;ved=0ahUKEwj1z6GFjPPXAhWiAJoKHWBwCMYQFgg7MAI&amp;url=https://www.blackhat.com/presentations/bh-usa-00/Ron-Gula/ron_gula.ppt&amp;usg=AOvVaw0atDOmktQHu-zmOZBBZZfO)，[2](https://www.alertlogic.com/blog/ids/ips-signature-bypassing-(snort)，[3](https://github.com/ahm3dhany/IDS-Evasion)。



## 五、签名检测所消耗的资源

如前所述，签名检测速度是开发者所要考虑的重要因素，自然，签名越多，扫描所需的CPU等资源就越多。“golden mean”规则推荐在Suricata系统下，增加一CPU全负载应该等于1000个签名*500Mbps网络流量。

[![](https://p0.ssl.qhimg.com/t0112a3225f4dac4c82.png)](https://p0.ssl.qhimg.com/t0112a3225f4dac4c82.png)<br>
它取决于签名数量和网络流量。虽然这个公式看起来不错，但它没有发现签名检测可能很快或很慢，并且流量可能非常多样化的事实。那么如果一个检测缓慢的签名遇到流量堵塞，会发生什么呢？<br>
Suricata可以记录签名的性能数据。日志收集检测最慢签名的数据，并生成一个列表，指定执行时间，以时钟周期为单位-CPU占用时间和执行的检查次数。最慢的签名位于顶部。

[![](https://p5.ssl.qhimg.com/t01743ca0152ecf7474.png)](https://p5.ssl.qhimg.com/t01743ca0152ecf7474.png)<br>
红线圈出的部分签名是检测起来非常耗时的，该清单不断更新;不同的流量配置文件肯定会列出其他签名。这是因为签名通常由检查规则的一个子集组成，例如搜索以特定顺序排列的子字符串或正则表达式。检查网络数据包或数据流时，签名会检查其全部内容以获取所有有效组合。因此，对同一个签名的检查树可以具有更多或更少的分支，并且执行时间将根据分析的流量而变化。因此，开发人员的任务之一就是优化签名以适应任何类型的流量。<br>
如果IDS未能正确实施并且无法检查所有网络流量时，会发生什么呢？一般来说，如果CPU内核的平均负载超过80％，就意味着IDS已经开始跳过一些数据包检查了。核心上的负载越高，越多的网络流量检查就会被跳过，恶意行为被忽视的可能性就越大。<br>
如果签名花费太多时间来尝试增加检查网络数据包的效果时会怎样？这样的操作方案会迫使IDS忽略数据包以及可能潜在的攻击。我们已经在实时流量中列出了热门（耗时多）签名，我们将尽力扩大他们的影响。



## 六、开始攻击实战

上述列表中的一个签名是用来检测流量中企图利用漏洞CVE-2013-0156（RoR YAML反序列化代码执行）的。

[![](https://p5.ssl.qhimg.com/t01bb8ff2f066c496e1.png)](https://p5.ssl.qhimg.com/t01bb8ff2f066c496e1.png)<br>
IDS会检查所有针对公司Web服务器的HTTP流量是否存在以下严格的字符串序列—“type”，’yaml”，’!Ruby”—并使用正则表达式进行检查。<br>
在我们着手生成“恶意”流量之前，我会提出一些可能有助于我们研究的假设：

> <ul>
- 找到匹配的子字符串比证明没有找到匹配的子字符串耗时更短。
- 对于Suricata系统来说，正则表达式匹配检查比直接搜索检查字符串更耗时。
</ul>

也就是说如果我们想要签名检查的时间更长，这些检测匹配就应该是不成功的，并让其使用正则表达式。

[![](https://p5.ssl.qhimg.com/t0129a29b4ac1c26a2f.png)](https://p5.ssl.qhimg.com/t0129a29b4ac1c26a2f.png)<br>
为了让其使用正则表达式检查，我们在数据包中构造三个拼接在一起的子串。<br>
接下来，我们尝试按顺序组合它们并运行IDS来执行检查。为了从文本中构建带有Pcap格式的HTTP流量文件，我使用了[Cisco Talos的file2pcap](https://github.com/Cisco-Talos/file2pcap)工具:

[![](https://p2.ssl.qhimg.com/t0126ca407850bb64ab.png)](https://p2.ssl.qhimg.com/t0126ca407850bb64ab.png)<br>
另一个日志文件，keyword_perf.log，可以帮助我们看到checks链成功地被正则表达式匹配（content matches—3），然后失败（PCRE matches—0）。如果之后我们想从资源密集的PCRE检查中受益，我们就需要彻底地解析它并选择一些有效的流量攻击。

[![](https://p0.ssl.qhimg.com/t0111f3678a9314a23e.png)](https://p0.ssl.qhimg.com/t0111f3678a9314a23e.png)<br>
反向解析正则表达式的任务虽然易于手动执行，但很难将过程自动化。原因是它具有特定的反向引用或命名捕获组结构：我根本找不到任何方法来自动选择可以成功通过正则表达式的字符串。

[![](https://p1.ssl.qhimg.com/t01e9cba1b4d8ce2d7d.png)](https://p1.ssl.qhimg.com/t01e9cba1b4d8ce2d7d.png)<br>
以下构造是这种表达式所需的最小字符串。为了测试一个不成功的搜索比成功的搜索更耗费资源的理论，我们将修剪字符串中最右边的字符并再次进行正则匹配。

[![](https://p5.ssl.qhimg.com/t01f03a74def64fc877.png)](https://p5.ssl.qhimg.com/t01f03a74def64fc877.png)<br>
事实证明，同样的理论也适用于正则表达式：不成功的搜素比其成功的搜索进行了更多的步骤。在本次示例中，其中的差异大于50％。你可以在[这里](https://regex101.com/r/51ukhR/1)看到。<br>
通过对这个正则表达式的进一步研究，我们有了另一个重大发现。如果我们反复复制去除最后一个字符的最短字符串，IDS为了对其进行检查需要采取大量步骤去完成检测，其增长曲线是爆炸性的:

[![](https://p4.ssl.qhimg.com/t01da1aaa86079fbe40.png)](https://p4.ssl.qhimg.com/t01da1aaa86079fbe40.png)<br>
几十个这样的字符串的扫描时间已经在1秒左右，并且增加它们的数量有超时错误的风险。正则表达式中的这种效果被称为catastrophic backtracking（灾难性回溯）。有许多文章来专门讨论它。而且很多常见的产品中仍然有这种错误;例如，最近在[Apache Struts](https://cwiki.apache.org/confluence/display/WW/S2-050)框架中就存在这样的问题。<br>
让我们把得到的字符串用Suricata进行检查:

[![](https://p1.ssl.qhimg.com/t011bddf4da251ec0ea.png)](https://p1.ssl.qhimg.com/t011bddf4da251ec0ea.png)<br>
然而，IDS并没有发现灾难性回溯，而且仅仅有一百万个ticks。在调试和检查Suricata IDS源代码以及其中使用的libpcre库之后，我偶然发现了这些PCRE限制:

> <ul>
- MATCH_LIMIT DEFAULT = 3500
- MATCH_LIMIT_RECURSION_DEFAULT = 1500
</ul>

这些限制在许多正则库中都存在，用来避免灾难性回溯的发生。在正则匹配占主导地位的WAF中也可以找到同样的限制。当然，这些限制可以在IDS配置中进行更改，但默认情况下不会改变，并且并不推荐更改它们。<br>
看来，只使用正则表达式不会帮助我们达到预期的效果。但是如果我们使用IDS检查包含此内容的网络数据包，该怎么办？

[![](https://p0.ssl.qhimg.com/t01927a0fb161cf9083.png)](https://p0.ssl.qhimg.com/t01927a0fb161cf9083.png)在这种情况下，我们得到以下日志值:

[![](https://p4.ssl.qhimg.com/t01718fb1495d07025c.png)](https://p4.ssl.qhimg.com/t01718fb1495d07025c.png)<br>
有4个checks，后来变成7个只是因为重复初始字符串。虽然机制尚不清楚，但如果我们进一步复制字符串，所期望的checks数量应该会继续增加。最后，我得到了以下值:<br>
content **1508** **1507**<br>
pcre **1492** 0<br>
总的来说，无论签名检查了什么内容，子字符串和正则表达式的检查次数都不会超过3000次。很显然，IDS本身也有一个内部限制器，它的名称为检查递归限制，默认设置为3000。因为存在PCRE，IDS限制以及一次性内容大小检测，我们可以通过修改内容并使用snowballing正则表达式进行检查，可以得到以下结果:<br>
content 3626 1508 1507<br>
pcre **1587144** 1492 0<br>
尽管一个正则表达式检查的复杂性没有改变，但这种检查的数量已经达到了1500。将检查次数乘以在每次检查上花费的平均时钟周期数，我们得到想要的三百万ticks。

[![](https://p4.ssl.qhimg.com/t01aa5447aa27495f1d.png)](https://p4.ssl.qhimg.com/t01aa5447aa27495f1d.png)<br>
这已经超过了千倍！该操作仅需要curl程序来生成最小HTTP POST请求。如下所示:

[![](https://p2.ssl.qhimg.com/t017b0d7ce24c2b2ade.png)](https://p2.ssl.qhimg.com/t017b0d7ce24c2b2ade.png)<br>
重复模式下HTTP字段和正文的最小集合。<br>
这样的内容并不能无限放大来造成IDS花费大量资源检查的局面，因为虽然在其内部TCP段被加入到单个流中，但无论多大的流和收集到的HTTP包都并没有被完全检查。相反，他们被检查的大小仅仅是约为3-4千字节的小块。要检查的段的大小以及检查的深度可以在config中设置（IDS中的所有内容都可以在这里设置）。从端到端传输的数据包段大小在“浮动”，以避免对这些段的分片攻击 — 当攻击者知道默认段的大小时，就会拆分发送的网络数据包，以便将攻击分为两个相邻段，从而绕过签名检测。<br>
所以，我们刚刚掌握了一个强大的武器，来强迫IDS加载从而使得CPU达到过载的程度（3,000,000,000 CPU ticks）。<br>
实际获得的数字大约是CPU平均操作1秒。基本上，通过发送大小为3 KB的HTTP请求，我们使得IDS加载整整一秒。IDS中的核心越多，它可以同时处理的数据流就越多。

[![](https://p3.ssl.qhimg.com/t0173baaea7c6967cb3.png)](https://p3.ssl.qhimg.com/t0173baaea7c6967cb3.png)<br>
请记住，IDS不会闲置，通常会花费一些资源监视后台网络流量，从而降低攻击阈值。<br>
使用8/40 Intel Xeon E5-2650 v3 CPUcores（2.30 GHz），无其他流量（8个CPU内核均已100％加载）的IDS按照配置指标IDS进行正常工作时，阈值仅为250 Kbps。这就是设计用于处理数千兆网络流的系统，即thousands of times greater。<br>
为了利用这个特定的“签名”，攻击者只需每秒向受保护的Web服务器发送大约10个HTTP请求，以逐渐填充IDS的网络包队列。当缓冲区填满时，数据包开始绕过IDS，攻击者可以使用任何工具或进行任意攻击，同时不被检测系统察觉。恶意流量的持续发送会使IDS瘫痪，直到流量停止轰击内部网络;而对于短期攻击，攻击者可以利用这些数据包发送致命的恶意流量，并在短时间内使检测系统失效。<br>
目前的机制无法检测慢签名导致的问题：尽管IDS有一个分析代码，但系统无法区分这是恶意的速度慢还是只是检测速度很慢的签名。由于缺少相关内容，慢签名触发也不会发出任何信号。<br>
你还记得checks数量无法解释的增加吗？确实存在IDS错误，导致多余checks数量增加。该漏洞的名称为CVE-2017-15377，现已在Suricata IDS 3.2和4.0中修复。<br>
上述方法对于一个特定签名尤其好用，这个签名存在于开放的签名集中，默认启用，但清单顶部还在不断出现新的签名，而另一些则继续等待与其匹的的配流量。Snort和Suricata的签名描述语言为开发人员提供了许多方便的工具，例如base64解码，内容跳转和数学运算。其他checks组合也可能导致资源消耗爆炸性增长。细致地监控性能数据却也成为了这个漏洞实现的跳板。在CVE-2017-15377问题得到解决后，我们再次启动Suricata来检查我们的网络流量，还是看到了完全相同的图片:日志顶部同样的签名列表，只是具体数字不同。这表明这种签名以及利用它们的方式依然很多。<br>
不仅是IDS，反病毒软件，WAF以及许多其他的系统都是基于这种签名搜索的方式。因此，这种方法也可以应用于其他对搜索处理不当的系统当中。它可以间接地阻止检测系统检测恶意行为。安全工具或是异常检测器都无法检测到相关的网络活动。作为一个实验，在您的检测系统中启用分析设置 – 并注意性能日志的顶部。

[![](https://p5.ssl.qhimg.com/t01241c276d24f1da55.png)](https://p5.ssl.qhimg.com/t01241c276d24f1da55.png)
