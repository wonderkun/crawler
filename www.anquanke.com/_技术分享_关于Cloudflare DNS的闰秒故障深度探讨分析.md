> 原文链接: https://www.anquanke.com//post/id/85246 


# 【技术分享】关于Cloudflare DNS的闰秒故障深度探讨分析


                                阅读量   
                                **81227**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：cloudflare.com
                                <br>原文地址：[https://blog.cloudflare.com/how-and-why-the-leap-second-affected-cloudflare-dns/](https://blog.cloudflare.com/how-and-why-the-leap-second-affected-cloudflare-dns/)

译文仅供参考，具体内容表达以及含义原文为准



**[![](https://p3.ssl.qhimg.com/t0104ae105cdc25ec2f.jpg)](https://p3.ssl.qhimg.com/t0104ae105cdc25ec2f.jpg)**

**翻译：**[**shan66******](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：180RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**前言**

2016年12月31日增加了一闰秒，31日11点59分59秒之后不是2017年，而是59分60秒。就在这个时候，在Cloudflare系统深处的一个自定义RRDNS软件出现了一个问题：一个数字变为了负数，但是按理说，它的最低值应该是零。稍后，这个负值就引起了RRDNS出现问题。该问题是通过Go语言的恢复功能捕获的。最后的结果就是，导致托管在Cloudflare上的某些网络资源无法正常进行DNS解析。

该问题只对使用的CNAME DNS记录的Cloudflare客户产生了影响，并且只影响到了Cloudflare 102个数据中心中的少数机器。在针对Cloudflare的DNS查询峰值时刻，大约有0.2％的查询受到了影响，同时，对于Cloudflare的所有HTTP请求中，只有不到1％的请求遇到了错误。

这个问题很快就被发现了。并且，大部分受影响的机器在90分钟内就得到了修复，到了UTC 06:45，修复程序已向全球用户发布。我们对客户受到了影响深表歉意，同时，为了让人们弄明白这个问题的来龙去脉，我们认为有必要把具体的原因和原理讲清楚。

<br>

**关于Cloudflare DNS的背景知识 **

Cloudflare的客户是通过我们的DNS服务来为其域名提供DNS查询的权威答案的。他们需要告诉我们其原始Web服务器的IT地址，以便我们联系该服务器来处理非缓存请求。要想完成此项工作，可以借助两种方式：要么输入与名称有关的IP地址（比如example.com的IP地址是192.0.2.123，并作为一条A记录来输入），要么输入CNAME（比如example.com是origin-server.example-hosting.biz）。

下图显示的是一个测试网站，它不仅提供了theburritobot.com的A记录，还提供了www.theburritobot.com的CNAME，它直接指向Heroku。

[![](https://p2.ssl.qhimg.com/t015ec8239e99d2581f.png)](https://p2.ssl.qhimg.com/t015ec8239e99d2581f.png)

当客户选用CNAME这种方式时，Cloudflare有时需要使用DNS查询原始服务器的实际IP地址。它是使用标准的递归DNS自动执行这项操作的。导致本次故障的软件bug，就位于执行这个CNAME查询的代码中。

在系统内部，执行CNAME查询时，Cloudflare运行DNS解析器，查询来自互联网的DNS记录，然后，RRDNS会跟这些解析器进行交互，以便获得IP地址。RRDNS会跟踪记录内部解析器的性能情况，并对可能的解析器（我们每个数据中心都会运行多个解析器，以确保冗余性）进行加权选择，选择性能最好的那个解析器。其中一些解析最后在数据结构中记录下了闰秒期间的一个负值。

稍后，这个负数被传递给了进行加权选择的代码，从而引发了问题。实际上，负数是由于闰秒和平滑处理（smoothing）这两个因素共同作用的结果。

<br>

**程序员过于盲目相信时间值了 **

之所以出现影响我们DNS服务的那个错误，根本原因在于程序员坚信表示时间的值不会倒退。以我们为例，一些代码想当然地以为：在最糟糕的情况下，两个时间之间的时差总是为零。

RRDNS软件是用Go编写的，并且使用Go的time.Now()函数来获取时间。遗憾的是，这个函数无法保证单调性。Go目前没有提供单调的时间源（详情请访问[https://github.com/golang/go/issues/12914](https://github.com/golang/go/issues/12914)）。

在评估用于CNAME查询的上游DNS解析器的性能时，RRDNS使用了下列代码： 



```
// Update upstream sRTT on UDP queries, penalize it if it fails
if !start.IsZero() `{`
    rtt := time.Now().Sub(start)
    if success &amp;&amp; rcode != dns.RcodeServerFailure `{`
        s.updateRTT(rtt)
    `}` else `{`
        // The penalty should be a multiple of actual timeout
        // as we don't know when the good message was supposed to arrive,
        // but it should not put server to backoff instantly
        s.updateRTT(TimeoutPenalty * s.timeout)
    `}`
`}`
```

在上面的代码中，如果time.Now()返回的时间早于start中的时间（这个值是早先调用time.Now()时设定的），rtt可能是负数。

如果时间往前进，该代码会一切正常。不幸的是，我们将我们的解析器调整得非常快，这意味着它们在几毫秒内进行应答是很正常的事。但是，如果恰好进行解析时，时间后退了一秒，那么解析时间就会成为负值。

实际上，RRDNS并非通过单个测量值来衡量每个解析器的性能，而是通过多个测量值，然后对它们进行平滑处理。所以，单个测量值不会引起RRDNS认为解析器在负时间内工作，但是对多个测量值进行平滑处理后，这个值最终就可能变成负值。

当RRDNS选择上游解析CNAME时，它使用了一种加权选择算法。相应代码取得上游时间值之后，会并将它们提供给Go的rand.Int63n()函数。如果rand.Int63n的参数为负数， 就会立即出现问题。这就是造成RRDNS问题的根本原因。

（除此之外，程序员在时间方面还有许多错误认识）。

<br>

**一个字符搞定漏洞 **

当我们使用非单调时钟源的时候，一个需要注意的问题是，始终检查两个时间戳之间的差值是否为负数。如果出现负数，除非时钟停止倒回，否则就不可能准确地确定时间差。

在这个补丁中，我们让RRDNS忘记当前的上游性能，并且如果时间向后跳过的话，就让它再次正常化。这样就可以防止将负数传递给服务器的选择代码，从而避免了在联系上游服务器之前就抛出错误信息了。

我们使用的修复方法是防止在服务器选择代码中记录负值。之后，重新启动所有RRDNS服务器，就能解决这个问题了。

<br>

**时间表**

下面是闰秒错误相关事件的完整时间表：

2017-01-01 00:00 UTC 出现影响

2017-01-01 00:10 UTC 上报给工程师

2017-01-01 00:34 UTC 确认问题

2017-01-01 00:55 UTC 缓解措施部署到一个canary节点上，并加以核实

2017-01-01 01:03 UTC 缓解措施部署到canary数据中心，并加以核实

2017-01-01 01:23 UTC 修复程序部署到大多数受影响的数据中心

2017-01-01 01:45 UTC 修复程序部署到主要的数据中心

2017-01-01 01:48 UTC 修复程序部署到每个地方

2017-01-01 02:50 UTC 修复程序在大多数受影响的数据中心发挥作用

2017-01-01 06:45 UTC 影响已消除 

下面的图表展示了每个Cloudflare数据中心的错误率（一些数据中心比其他数据中心受到的影响要大一些），以及部署修复代码后，错误率的快速下降情况。我们在部署修复程序时，优先照顾错误最多的那些数据中心。

[![](https://p2.ssl.qhimg.com/t01189df74a5ad22a2a.png)](https://p2.ssl.qhimg.com/t01189df74a5ad22a2a.png)

<br>

**小结**

对于这个问题给客户带来的影响，我们深表歉意，与此同时，我们正在对所有代码进行相应的检查，以确保闰秒不会对其他代码产生影响。
