> 原文链接: https://www.anquanke.com//post/id/85355 


# 【技术分享】利用ImageMagick命令执行漏洞拿下Facebook四万美元奖金


                                阅读量   
                                **84379**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：4lemon.ru
                                <br>原文地址：[http://4lemon.ru/2017-01-17_facebook_imagetragick_remote_code_execution.html](http://4lemon.ru/2017-01-17_facebook_imagetragick_remote_code_execution.html)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p5.ssl.qhimg.com/t01fa03da4979ce8c58.jpg)](https://p5.ssl.qhimg.com/t01fa03da4979ce8c58.jpg)



**翻译：**[**pwn_361******](http://bobao.360.cn/member/contribute?uid=2798962642)

**预估稿费：100RMB**

**投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿**



**前言**

我相信很多人都知道[ImageMagick](https://www.imagemagick.org/)和[它存在的漏洞](https://imagetragick.com/)，这个漏洞发现于2016年四月底，同时，由于许多插件都依赖于这个ImageMagick库，因此，这个漏洞的影响范围很大。有证据表明，关于这个漏洞的信息，发现它的研究人员是知道的，ImageMagick开发团队的人也知道，但是，糟糕的是，一些其它的人(坏人)也知道了这个漏洞，在2016年5月3日，在互联网上发现了这个漏洞的POC。许多研究人员发现了这个问题，而且应用程序还没有及时更新。但由于一些未知的原因，我不在其中，但这是在5月份。

<br>

**漏洞分析**

直到十月的一个星期六，我对一些大的服务(不是Facebook)进行了测试，当时一些重定向让我关注到了Facebook。这是一个《分享到Facebook》对话框：

[![](https://p4.ssl.qhimg.com/t01b33d8197283f385f.png)](https://p4.ssl.qhimg.com/t01b33d8197283f385f.png)

链接是：

[https://www.facebook.com/dialog/feed?app_id=APP_ID&amp;link=link.example.tld&amp;picture=http%3A%2F%2Fattacker.tld%2Fexploit.png&amp;name=news_name&amp;caption=news_caption&amp;description=news_descriotion&amp;redirect_uri=http%3A%2F%2Fwww.facebook.com&amp;ext=1476569763&amp;hash=Aebid3vZFdh4UF1H](https://www.facebook.com/dialog/feed?app_id=APP_ID&amp;link=link.example.tld&amp;picture=http%3A%2F%2Fattacker.tld%2Fexploit.png&amp;name=news_name&amp;caption=news_caption&amp;description=news_descriotion&amp;redirect_uri=http%3A%2F%2Fwww.facebook.com&amp;ext=1476569763&amp;hash=Aebid3vZFdh4UF1H) 

大家可以看到，如果我们仔细看，我们可以看到在URL中有一个“picture”参数。但是在上面提到的页面内容中，这并不是图片URL，例如：

[![](https://p1.ssl.qhimg.com/t016a834f9bb53fcd4a.png)](https://p1.ssl.qhimg.com/t016a834f9bb53fcd4a.png)

[https://www.google.com/images/errors/robot.png](https://www.google.com/images/errors/robot.png) 

变成了：

[![](https://p4.ssl.qhimg.com/t01263a32bc1b889584.png)](https://p4.ssl.qhimg.com/t01263a32bc1b889584.png)

[https://external.fhen1-1.fna.fbcdn.net/safe_image.php?d=AQDaeWq2Fn1Ujs4P&amp;w=158&amp;h=158&amp;url=https%3A%2F%2Fwww.google.com%2Fimages%2Ferrors%2Frobot.png&amp;cfs=1&amp;upscale=1&amp;_nc_hash=AQD2uvqIgAdXgWyb](https://external.fhen1-1.fna.fbcdn.net/safe_image.php?d=AQDaeWq2Fn1Ujs4P&amp;w=158&amp;h=158&amp;url=https%3A%2F%2Fwww.google.com%2Fimages%2Ferrors%2Frobot.png&amp;cfs=1&amp;upscale=1&amp;_nc_hash=AQD2uvqIgAdXgWyb) 

我首先考虑到了一些关于[SSRF](https://docs.google.com/document/d/1v1TkWZtrhzRLy0bYXBcdLUedXGb9njTNIJXa3u9akHM/edit)的问题。但是测试显示，这个URL中的参数请求来自于31.13.97.*网络，通过“facebookexternalhit/1.1”参数，如下：

[![](https://p0.ssl.qhimg.com/t0130346cb2e8ecce06.png)](https://p0.ssl.qhimg.com/t0130346cb2e8ecce06.png)

它看起来像独立服务器的正常请求。我开始深入挖掘。在对这个参数进行一些测试后，我很失望，没有一个成功，[ImageTragick](https://imagetragick.com/)是最后一点希望。如果你不熟悉这个问题或有点懒惰，这里有一[POC](https://github.com/ImageTragick/PoCs)链接。下面是一个简单的exploit.png载荷：

[![](https://p3.ssl.qhimg.com/t01a5a79b873cd5db81.png)](https://p3.ssl.qhimg.com/t01a5a79b873cd5db81.png)

但是当我监听端口时，什么也没发现：

[![](https://p0.ssl.qhimg.com/t016697f1d6ddb40bff.png)](https://p0.ssl.qhimg.com/t016697f1d6ddb40bff.png)

不过，如果有一些防火墙限制呢？-我问我自己。

好吧，通常一些公司会过滤正常的请求，但是不会过滤DNS，让我们再试一个载荷：

[![](https://p3.ssl.qhimg.com/t01a6187fb929c5297a.png)](https://p3.ssl.qhimg.com/t01a6187fb929c5297a.png)

结果是：

[![](https://p5.ssl.qhimg.com/t01f2fb181c32e06cdb.png)](https://p5.ssl.qhimg.com/t01f2fb181c32e06cdb.png)

这个IP是谁的呢？看下图：

[![](https://p5.ssl.qhimg.com/t0153af4488d0ac0a5b.png)](https://p5.ssl.qhimg.com/t0153af4488d0ac0a5b.png)

成功了！

让我们总结一下，应用程序的工作流程是：

获得“picture”参数，并向它发出请求，这个请求是正常的，没有漏洞。

收到一个图片，这个图片经过了converter的转换，而它使用了有漏洞的ImageMagick库。

说实话，我试图找到一个通用的方法来利用这个HTTP请求，但是经过简短的测试后，我发现所有向外的端口都被关闭了，我花了很长的时间去找一个能打开的，没有成功，我需要找到另一种能让POC有效的方法。

载荷：

[![](https://p1.ssl.qhimg.com/t01d51a5c7301ed50d6.png)](https://p1.ssl.qhimg.com/t01d51a5c7301ed50d6.png)

回应是：

[![](https://p3.ssl.qhimg.com/t019c8f1d588a61dba2.png)](https://p3.ssl.qhimg.com/t019c8f1d588a61dba2.png)

下面是“id”返回的信息：

[![](https://p0.ssl.qhimg.com/t01b778a5e2d4adb614.png)](https://p0.ssl.qhimg.com/t01b778a5e2d4adb614.png)

为了充分证明存在这个漏洞，我给Facebook安全团队提供了“cat/proc/version”的结果，在这里我就不公布它的结果了。

根据Facebook负责任的漏洞披露政策，我没有进行更深的研究。

我和Facebook安全团队的Neal研究员讨论了最初的报告，“cat/proc/version | base64”可能更好，同时，一些更深层次的研究表明，“base32”在包括DNS隧道的各种技术中是比较常用的(请看：https://www.sans.org/reading-room/whitepapers/dns/detecting-dns-tunneling-34152)。

我很高兴成为攻破Facebook的人之一。

<br>

**时间线**

16 Oct 2016, 03:31 am: 初始报告;

18 Oct 2016, 05:35 pm: Neal向我要使用的POC；

18 Oct 2016, 08:40 pm: 我发送了一个POC并提供了额外的信息；

18 Oct 2016, 10:31 pm: Neal确认了漏洞；

19 Oct 2016, 12:26 am: Neal说正在修复漏洞；

19 Oct 2016, 02:28 am: Neal通知我说漏洞已经修复；

19 Oct 2016, 07:49 am: 我回答说，确认漏洞修补，并要求披露时间表；

22 Oct 2016, 03:34 am: 尼尔回答披露时间表； 

28 Oct 2016, 03:04 pm: 4万美元的奖励发放；

16 Dec 2016: 披露批准；
