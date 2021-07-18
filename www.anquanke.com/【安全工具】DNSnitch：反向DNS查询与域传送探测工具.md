
# 【安全工具】DNSnitch：反向DNS查询与域传送探测工具


                                阅读量   
                                **102397**
                            
                        |
                        
                                                                                                                                    ![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：thevivi.net
                                <br>原文地址：[https://thevivi.net/2016/11/17/dnsnitch-reverse-ns-lookups-zone-transfers/](https://thevivi.net/2016/11/17/dnsnitch-reverse-ns-lookups-zone-transfers/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85887/t012f4a058d6fb9fd83.jpg)](./img/85887/t012f4a058d6fb9fd83.jpg)**

****

翻译：[村雨其实没有雨](http://bobao.360.cn/member/contribute?uid=2671379114)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

近期对Dyn的DDoS攻击的事件让我把目光放到了DNS上，黑客们一次又一次证明了成功实施DDoS攻击的最佳方式，就是攻击DNS服务器。

作为一名渗透测试工程师，我在评估系统安全时确实能够经常看到域名解析服务器，这一点在信息搜集阶段尤为明显。我们现在仍然能够时不时的看到一些允许域传送的公共域名服务器，显然这是个隐患。但我还从没有把DNS服务器作为过一个实际的攻击目标，我的客户也都不愿意在付费测试时允许工程师瘫痪掉他们的网络服务。

对Dyn的DDoS攻击是个大麻烦，因为Dyn是主要的DNS解析服务供应商，对Dyn的攻击造成了一批知名站点的服务中断，其中包括Twitter, Paypal, Reddit, Github, Spotfy等

这不禁使我思考，如果我是一名攻击者，要找到最合适的域名解析服务器进行攻击，我该怎么做，我应该选择哪一台域名解析服务器。查询目标所使用的域名解析服务器非常容易，但是如果我的目标是域名服务器，我要对域名解析服务器进行DDoS攻击，那么我就应该进行相反的查询，找出一个域名解析服务器提供服务的所有域名。

<br>

**反向NS查询**

Google结果告诉我要进行反向域名解析查询，只要我们能够找到一个域名服务器，我们就能够查询到它提供服务的所有独立域名。反向域名解析查询是如何生效的呢，我在Server Fault上找到了最好的答案：

域文件访问：一些注册处会授予注册商或其他团体访问域文件的权限。这也就能让我们非常容易地确定在这些空间中哪些域有访问DNS服务器的权限。但是在我研究时发现，现在提供访问域文件权限的注册商并不常见。这样一来，尽管这种方法是最可靠的，也并没有被广泛使用。

被动DNS：被动DNS通过ISP的递归DNS服务器流量检查和根据所见重建区域数据来实现目的。尽管这种方法会消耗大量资源，并且数据库中的数据可能过时，它还是被作为一种有效手段广泛使用。我将会在下文继续谈论这种方法。

<br>

**反向NS查询工具**

我做的第一件事就是去搜索能够执行反向NS查询命令的命令行工具。我确实也找到了一些或免费或付费提供这项服务的网站，由于我本身就是安全专家，我还是倾向于使用免费工具，也花了不少时间去研究。

**1. Gwebtools**

我首先要介绍的就是gwebtools的域名检测工具。正如它承诺的一样，只要给它一个域名服务器，它就能列出可用的所有域名。唯一的缺陷就是它只能提供.com和.net结尾的域名。它的工作原理就是运营商提供了一套监测.com和.net域变化的系统，并且每月更新一次。

[![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016d78559b642e6461.png)

**2. Viewdns.info**

接下来我要介绍viewDNS.info提供的NS反向查询工具。我更喜欢这个工具，因为它监测的域比ns-spy更多，能够获得比gwebtool更多的结果。他们提供了API，能让我们把这项工具整合到自己的工具中。他们甚至会售卖收集到的域信息。

[![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cd42805cea9d8163.png)

**3. Domain Tools**

最后登场的是Domain Tools的NS反查工具。这个工具并非免费工具，在进行查询后，你能够得到一个免费的结果样例，但是想要得到完整的结果，要么以每月$99的价格缴纳会员费，要么以$70的非会员价去购买结果

[![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f0f5dd19af77c864.png)

据我所知，这项工具提供的查询结果比上两个工具的结果更加丰富，以ns1.safaricombusiness.co.ke这一域名服务器为例，查询结果如下：

gwebtools发现1017个域

[![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01dacd8840e9dc2d77.png)

viewdns.info发现2563个域

[![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f377f1980c6aea59.png)

Domain Tools找到9814个域

[![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01894fc351a3e0fe3c.png)

<br>

**DNSnitch**

上面提到的在线工具虽好，但是依旧不能满足我的需求，我需要的是一个能够不离开终端就能进行NS反向查询的工具。由于我们能够访问注册管理机构的域文件，我能想到的最佳方案就是利用上面提到的一个网站来获得我想要的结果。

最终，在gwebtools和viewdns.info之间，我选择了后者，理由如下：

Viewdns.info能够监视更多地域，且能提供更多的结果，这从查询样例中就能看出来。

Viewdns.info的输出更容易被解析，它所有的查询结果都是输出在单个页面的，而gwebtool的输出在多个页面，对结果进行分析和在终端输出会变得更麻烦。

DNSnitch工具是一个Python脚本，能够向viewdns.info的NS反向查询工具发送请求，并且将结果输出到终端上

[![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0162a5296c011491a8.png)

[![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012482097e7060a188.png)

<br>

**域传送**

当我在一些公共域名服务器进行测试时，我发现有两个域名服务器允许所有域使用它们进行域传送（现在这一问题仍然存在）

这里的资料说明了什么是域传送，以及为什么人们永远不应该在公共域名服务器上允许域传送。总而言之，域传送能够让网络结构探测变得容易的多，就好比我们直接走进目标的大门，向网络部门主管要到了一张详尽的IP列表，再从大门走出去。你并不会因此立刻被入侵，但是它能让你的敌人获取到很多重要信息，而这些信息在后期攻击阶段至关重要。域传送漏洞已经被我们知晓多年，现在这种问题仍然存在让我非常惊讶。

根据viewdns.info的查询结果，我发现的在非洲的域名服务器为2000多个域提供了服务。而根据Domain Tools的资料，这个数字则是7000多。

[![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0112eae7c3c12bccf5.png)

正因如此，我觉得我应该为DNSnitch添加一点更有趣的功能。如果在运行DNSnitch时添加了-zt参数，程序不会在列出所有域后停止，而是去用dig(domain information groper)继续探测所有发现的域是否能够进行域传送(域传送只能通过指定的域名服务器去尝试)。

我在上面的域名服务器试用了这个脚本，结果相当不错。尽管不会命中每个域，但是最终成功的域还是很多的。

[![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e1cf09562b23dccb.png)

[![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0154c6ea9db01ca62b.png)

[![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c9012104eaf9e085.png)

[![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fce5d298d181fadd.png)

<br>

**axfr.py**

我又写了一个脚本，它能将接收一个域列表，并尝试针对指定的域名服务器进行域传送。如果有人已经有了一个域列表，想要测试域传送漏洞，也许这就能派上用场。您可以在这里下载axfr.py

[![](./img/85887/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ecf2228c1c8f1c34.png)

<br>

**总结**

DNS的将遇到的麻烦还远远没有结束，也许眨眼之间一次DDoS就能让主流网站或公共服务中断，也许眨眼之间域名服务器就会停止对某个组织的公共设施的服务。

如果您是DNS管理员，请加固您的服务器，谨防DDoS攻击，禁止域传送。现在是2016年了，我们真的不应该再看到这个了。我将向上述域名服务器的管理员发送一封邮件报告漏洞，希望他们能尽快修复。祝大家狩猎愉快~
