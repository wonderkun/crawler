> 原文链接: https://www.anquanke.com//post/id/85219 


# 【技术分享】采用独特域名生成算法的Tofsee僵尸网络


                                阅读量   
                                **119720**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：govcert.admin.ch
                                <br>原文地址：[https://www.govcert.admin.ch/blog/26/tofsee-spambot-features-.ch-dga-reversal-and-countermesaures](https://www.govcert.admin.ch/blog/26/tofsee-spambot-features-.ch-dga-reversal-and-countermesaures)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p5.ssl.qhimg.com/t01155c014357b0b77e.png)](https://p5.ssl.qhimg.com/t01155c014357b0b77e.png)**

****

**翻译：**[**pwn_361******](http://bobao.360.cn/member/contribute?uid=2798962642)

**预估稿费：140RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**概述**

瑞士政府计算机应急响应中心(GovCERT)近日发现了Tofsee僵尸网络恶意软件的新样本，让他们感到惊讶是，Tofsee的域名竟然是由算法随机生成的，目前他们已经恢复出了算法的细节，并将未来12个月中可能出现的域名列入了黑名单。

<br>

**内容**

今天，我们发现了一个有趣的恶意软件样本，我们确认出这是Tofsee恶意软件，它试图在几分钟内发送数百封垃圾邮件，然而，这并不是它出现在我们视线中的原因（我们每天分析数以千计的恶意软件样本，很多都有这样的行为）。这个特定的样本引起我们注意的原因是它所使用的域名查询方法。它使用的域名似乎是用算法生成的，并且大约有一半域名是瑞士国家顶级域名（ccTLD）。

[![](https://p5.ssl.qhimg.com/t019443dfae74fff184.png)](https://p5.ssl.qhimg.com/t019443dfae74fff184.png)

使用域名生成算法(DGAs)的恶意软件是非常罕见的。

<br>

**分析**

我们分析的这个Tofsee样本有一个非常新的时间戳：“2016年12月16日星期五，07:09:11”。

[![](https://p1.ssl.qhimg.com/t01f5bee9fd36a14114.png)](https://p1.ssl.qhimg.com/t01f5bee9fd36a14114.png)

<br>

**生成种子**

下面我们来探讨DGA的具体过程。首先，计算1974年1月1日0时到现在的秒数（下图中 0x40A0A0），然后在 0x0040A0A8处，用这个值加再加上126230400秒(UNIX纪元到1974年1月1日的秒数)，实际上，通过上面的步骤得到了当前的UNIX时间。目前我们尚不清楚为什么要采用这种复杂的方法获取当前UNIX时间。这个Unix时间分别再除以四个整数，分别是60,60,24和7，最后得到的是从UNIX纪元到现在的周数。这个值用作域名生成算法的种子。因此域名的有效期是一周，按UTC时间，从每周四开始。

[![](https://p2.ssl.qhimg.com/t0185544fecff919a1a.png)](https://p2.ssl.qhimg.com/t0185544fecff919a1a.png)

在种子生成过程中还调用了一个伪随机数发生器(PRNG)，并将结果模10，得到0到9中的一个数。这个随机数发生器采用Borland C/C++编译器使用的标准线性同余算法。

[![](https://p1.ssl.qhimg.com/t01c9813169d3832dad.png)](https://p1.ssl.qhimg.com/t01c9813169d3832dad.png)

r2的初始值是几乎不可预测的：

[![](https://p0.ssl.qhimg.com/t01be79988ca60fdd70.png)](https://p0.ssl.qhimg.com/t01be79988ca60fdd70.png)



**DGA**

每次域名生成过程，共产生10个域名。

(域名级别是网址分类的一个标准，包括顶级域名、二级域名等。一个完整的域名由二个或二个以上部分组成，各部分之间用英文的句号"."来分隔，倒数第一个"."的右边部分称为顶级域名（TLD），顶级域名的左边部分字符串到下个"."为止称为二级域名（SLD），二级域名的左边部分称为三级域名，以此类推，每一级的域名控制它下一级域名的分配)

[![](https://p1.ssl.qhimg.com/t01d7327d2faff89b0c.png)](https://p1.ssl.qhimg.com/t01d7327d2faff89b0c.png)

在0x040A0FC 位置，根据种子生成一个随机字符串，例如周数。随后这个随机字符串在0x040A114又被复制了一次。例如：字符串dqg在这变成了dqgdqg，这个字符串的生成细节，待会我们回过头来再细讲。

生成第一个SLD时，用上面讲到的不可预测的随机数生成算法(0到9共10个数)，选取“a”到“j”之间(共10个字母)的随机字母，添加到上面的字符串后面，就生成了二级域名，如dqgdqgc.ch。然后，从选取的字母开始，DGA会依次选取a到j中的字母，比如，如果第一次选取了“c”，后面的依次就是“d”,“e”,“f”,“g”,“h”,“j”,“a”，最后是“b”,共10个域名。

前5个域名的顶级域名设为“.ch”，剩下的设置为“.biz”

下面，我们再来看一下0x040A0FC处的随机字符串(上面的dqgdqg)是怎么生成的。

[![](https://p5.ssl.qhimg.com/t01deaf9e39322b1636.png)](https://p5.ssl.qhimg.com/t01deaf9e39322b1636.png)

这段过程使用了最开始生成的种子r(周数),例如，根据1970年1月到现在的时间，换算成周数，利用周数得出随机字符串，如下：

[![](https://p0.ssl.qhimg.com/t015009018faedae77e.png)](https://p0.ssl.qhimg.com/t015009018faedae77e.png)

例如：2016年12月20日，根据UNIX纪元计算出的周数是r=2450，string1 = 2450%26+‘a’=g，r=2450/26=94，因此第一个字母是g，同时r!=0，继续循环，直到r=0时结束，最后依次得到的字母是:g、q、d。随后，随机字符串gqd被倒序为dqg。随后又被复制了一次，得到dqgdqg。

<br>

**程序实现**

下面是用python实现在DGA算法，根据给定的日期，能打印出所有20个可能的域名。需要注意的是，对于每一个正在运行的Tofsee恶意软件，只会用到其中的一个域名。

[![](https://p1.ssl.qhimg.com/t0100be0ff9a01cd285.png)](https://p1.ssl.qhimg.com/t0100be0ff9a01cd285.png)

下面是在日期设置为2016年12月20日时的所有20个可能的域名：

[![](https://p3.ssl.qhimg.com/t01da9a4cce9326e072.png)](https://p3.ssl.qhimg.com/t01da9a4cce9326e072.png)

<br>

**域名列表**

下表列出了未来52周的所有可能的域名，域名中括号包含了随机扩展，如dqgdqg`{`a..j`}`.`{`ch,biz`}`代表20个不同的域名。所有的时间都采用CET(中欧时间)时间。

[![](https://p1.ssl.qhimg.com/t01972ae56e8f1084f3.png)](https://p1.ssl.qhimg.com/t01972ae56e8f1084f3.png)

**采取的行动**

为了防止这种Tofsee僵尸网络操作者滥用瑞士域名空间(ccTLD .ch)，我们和瑞士国家顶级域名注册机构已经采取了进一步的措施，所有可能的DGA域名的组合，在注册状态处已经被设置为非注册状态。因此在未来12个月，任何由DGA算法生成的域名，都不会被注册。

<br>

**参考链接**

[https://www.easyaq.com/newsdetail/id/1946003877.shtml](https://www.easyaq.com/newsdetail/id/1946003877.shtml)
