> 原文链接: https://www.anquanke.com//post/id/86854 


# 【技术分享】通过伪造DNS响应绕过域名所有权验证


                                阅读量   
                                **120628**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：detectify.com
                                <br>原文地址：[https://labs.detectify.com/2017/09/11/guest-blog-bypassing-domain-control-verification-with-dns-response-spoofing/](https://labs.detectify.com/2017/09/11/guest-blog-bypassing-domain-control-verification-with-dns-response-spoofing/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01a5348ac1b92886a1.jpg)](https://p2.ssl.qhimg.com/t01a5348ac1b92886a1.jpg)

译者：[testvul_001](http://bobao.360.cn/member/contribute?uid=780092473)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言：**



我们的客座博主和Detectify众包团队黑客Evgeny Morozov将在本文中解释他是如何通过伪造DNS响应来绕过Detectify的域名所有权验证的。非常感谢Evgeny的突出贡献—众包团队中有这样的研究者很令人感到自豪。

当用户需要使用Detectify来扫描一个网站时，我们必须先验证他对这个域名的所有权（几乎所有的在线扫描都有这种验证）。其中的一种验证方式是在DNS的TXT记录中增加Detectify提供的字符串。当用户点击验证时，Detectify会执行一个DNS检查来确认是否存在验证字符串。下面我们来看看如果验证一个你并不拥有的域名会发生什么。 

<br>

**DNS 伪造背景**

****

DNS查询和响应通常都是通过UDP协议传输的，所以IP地址伪造可以让查询客户端认为攻击者所发的DNS响应是来自于正常DNS服务器的。当然查询客户端只会接受明显符合要求的响应，下面的几个项目必须符合要求：

1、源IP地址（DNS服务器）

2、目的IP地址（DNS客户端）

3、源端口（DNS服务器）-通常是53

4、目的端口（DNS客户端）-DNS请求的源端口

5、Transaction ID- 客户端产生的16 bit数字

6、Questions-本质上是复制的DNS查询请求

源地址和端口以及目的IP都是已知的，DNS “question”可以猜出来，或者从一个攻击者可以访问的地方复制一个真实的查询。现在唯一不能确定的就是目的端口和Transaction ID了。

九年前很多DNS客户端修复了可以预测源端口和Transaction ID的漏洞。猜测一个16bit的数字是完全可行的—因为只有65536种可能，攻击者完全可以在真实的DNS响应到达前给DNS客服端发送成千上万的假响应包。2008年的7月Dan Kaminsky披露了这个问题。随后DNS维护方就用完全随机的Transaction ID和端口修复了这个问题。所以这种攻击已经过时了，那么真是这样吗？

<br>



**通过验证**

****

我有一种预感，为了避免得到缓存数据，Detectify会执行自己的DNS查询，而不仅仅是使用系统的DNS解析工具。如果这样的话，它就仍可能还在使用可预测的Transaction ID和小范围的源端口。

为了测试我通过dnsmasq为我控制的域名搭建了一个简单域名服务器，并且在进行Detectify验证的时候抓了多次包。使用Wireshark打开抓的包，可以发现来自scanner.detectify.com的dns查询请求。源端口看起来是足够随机了，但是Transaction ID是不是有问题呢？

[![](https://p2.ssl.qhimg.com/t0166f25cdbfb6aaf10.png)](https://p2.ssl.qhimg.com/t0166f25cdbfb6aaf10.png)

 

**事情简单了！！！**

****

Transaction ID每次都是0，现在我准确的知道Detectify发出的DNS查询，所以伪造一个正确的DNS响应的唯一问题就是源端口。

<br>

**POC**

****

尽管现在我已经可以报告漏洞了，但是我想确定它是可利用的。一个理论漏洞和可利用的漏洞还是有差别的。

下面我们尝试验证example.com。创造一个伪造的DNS响应payload很简单：首先用tcpdump抓取一个真实的响应，然后手工改变域名。Nping工具可以用来发送这个响应并伪造原地址和端口：

 [![](https://p5.ssl.qhimg.com/t016bb66b631bc50628.png)](https://p5.ssl.qhimg.com/t016bb66b631bc50628.png)

上面的命令尝试尽可能快的发送伪造的DNS响应给scanner.detectify.com，它声称来自于199.43.133.53（example.com的真实域名服务器），设置的源端口范围在30000到39999。下面需要做的就是在我的笔记本上运行上述命令，并且在Detectify的网站上疯狂的不停的点击验证按钮。

事实上现在所有的ISP和数据中心都会在出口过滤伪造的数据包—防止它们离开自己的网络，并且有很好地理由。伪造的数据包最常见的用途是DDOS攻击，特别是DNS反射放大攻击。所以我需要一个不会做过滤的主机，并且攻击机和受害者之间的延迟必须尽可能的低，以提高伪造的响应在真实的响应之前到达的概率。

如何找到这样的一个主机就留给读者作为练习了。但是现在我可以自豪的说我已经是6个虚拟服务器的主人了，虽然其中的5个并没有什么卵用（所幸它们都很便宜）。在疯狂的点击Detectify网站的验证按钮后，我们终于得到了下面的提示：

 [![](https://p0.ssl.qhimg.com/t016ea2f2f06949b57b.png)](https://p0.ssl.qhimg.com/t016ea2f2f06949b57b.png)

成功了！



**总结：**

****

Detectify在报告后的三小时内修复了漏洞。


